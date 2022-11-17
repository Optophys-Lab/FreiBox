 /* Brice de la Crompe (Optophysiology lab / Diester lab) - Nov 2022
  * 
  *   Configuration 3 Hall sensors  (A, B and C)
  *   Their magnetic field define 6 different area (60 degrés)
  *   rotational adjustment in area 3 and 4 only
  *   Example of the measurment of the 'directionnal field' for A sensor (DF): 
  *           DF(A) = [analogRead(A)-analogRead(C)]-[analogRead(A)-analogRead(B)] 
  *           DF(A) = analogRead(B)-analogRead(C)        
       => if DF(A)>0 <=> Magnet is more oriented toward B than C  
       => if DF(A)<0 <=> Magnet is more oriented toward C than B 
       => The orientation of the magnet is defined in the following decision matrix by using this calculation method for the 3 sensors simultaneously 
  * 
  * 
  * Configuration:                                 Decision Matrix:
  * 
                ---                                       1     2     3     4     5     6
               - A - (Yellow)                     DF(A)  >0    >0    >0    <0     <0    <0
                ---                                           
                                                  DF(B)  <0    <0    >0    >0     >0    <0      
               6  1                                     
             5      2                             DF(C)  >0    <0    <0    <0     >0    >0              
     ---       4* 3**     ---                                    
    - C -                - B -                              
     ---                  ---                                       
   (Blue)               (Brown)                                 

Called in the code *10 and **11 to define when to adjust the position (>10)

 */    
int stepPin=6;
int dirPin=7;
int sleepPin=5;
int MS3pin=3;
int MS2pin=2;
int MS1pin=1;

int stepNumberForAdjustement = 100*16;//67; before 50 // Nema 17 = 1.8degre/step, so 67 steps = 120.6 degrees (=2 areas)! 

int sensorPinA = A5;  
int sensorPinB = A4;
int sensorPinC = A3;

int sensorValueA;
int sensorValueB;
int sensorValueC;

int decisionValueA=0;
int decisionValueB=0;
int decisionValueC=0;  

int numReadings=2; // Number of reading for average
int magnetDirection; // 
int previousMagnetDirection;
int previousDirection;

int needAdjustment=0;
int stopCounter=0;
// ======================================== // 
void setup() 
{
Serial.begin(9600);

pinMode(sensorPinA, INPUT);
pinMode(sensorPinB, INPUT);
pinMode(sensorPinC, INPUT);

pinMode(stepPin, OUTPUT);
pinMode(dirPin, OUTPUT);

pinMode(sleepPin, OUTPUT);
pinMode(MS1pin, OUTPUT);
pinMode(MS2pin, OUTPUT);
pinMode(MS3pin, OUTPUT);

digitalWrite(sleepPin, LOW);
digitalWrite(MS1pin, HIGH);
digitalWrite(MS2pin, HIGH);
digitalWrite(MS3pin, HIGH);


readPositionFunction();
magnetDirection=decisionFunction(decisionValueA,decisionValueB,decisionValueC);

}

void loop()
{

while(needAdjustment==0)
     {
     Serial.println("CheckingLoop");
//     Serial.println(" ");
//     Serial.println(magnetDirection);
//     Serial.print(" ");
//     Serial.print(magnetDirection);
//     Serial.println(" ");

   
     //delay(100);
     if(magnetDirection<10)
       {
       previousMagnetDirection=magnetDirection;
            
       }
     readPositionFunction();
     magnetDirection=decisionFunction(decisionValueA,decisionValueB,decisionValueC);  
     if(magnetDirection >= 10)
      {
      needAdjustment=1;
      digitalWrite(sleepPin, HIGH);
      break;
      }

   
///*     
   //   Serial.print("loop");
     Serial.print(" ");
     Serial.print(sensorValueA);
     Serial.print(" ");
     Serial.print(sensorValueB);
     Serial.print(" ");
     Serial.print(sensorValueC);     
     Serial.println(" ");
//*/     
     Serial.println("CheckingLoop");

 


   

     }


while((needAdjustment == 1) && (magnetDirection != 1) || (needAdjustment == 1) && (magnetDirection != 6) || (stopCounter=5))
     {     
     adjustPositionFunction(magnetDirection,previousMagnetDirection,stepNumberForAdjustement);  
     readPositionFunction();
     magnetDirection=decisionFunction(decisionValueA,decisionValueB,decisionValueC);  
//    Serial.println("AdjustmentLoop"); 
//     Serial.print(" ");
//     Serial.print(previousMagnetDirection);
//     Serial.print(" ");
//     Serial.print(magnetDirection);
//     Serial.println(" ");
 
 /*
     Serial.print("Outside loop");
     Serial.print(" ");
     Serial.print("Previous:");
     Serial.print(" ");      
     Serial.print(previousMagnetDirection);
     Serial.print(" ");
     Serial.print("New:");
     Serial.print(" ");           
     Serial.print(magnetDirection);
     Serial.print(" "); 
     Serial.print("Counter:");
     Serial.print(" ");    
     Serial.print(stopCounter);
     Serial.println(" ");


     Serial.print("AdjustmentLoop");


          Serial.print("loop");
     Serial.print(" ");
     Serial.print(sensorValueA);
     Serial.print(" ");
     Serial.print(sensorValueB);
     Serial.print(" ");
     Serial.print(sensorValueC);     
     Serial.println(" ");


     Serial.print("AdjustmentLoop");
     Serial.println(" ");
     Serial.println(magnetDirection);
*/     
     if(magnetDirection < 10)
       {
       previousMagnetDirection=magnetDirection;  
       //needAdjustment = 0;  
       }
     if((magnetDirection==1) ||(magnetDirection==6)) 
       {
       needAdjustment = 0;
       stopCounter=stopCounter+1;
       digitalWrite(sleepPin, LOW);    
       break; 
       }  
     else
       {
       }
     }
/*     Serial.print("Outside loop");
     Serial.print(" "); 
     Serial.print("Counter:");
     Serial.print(" "); 
     Serial.print(stopCounter);
     Serial.print(" ");
     Serial.print("needAdjustment:"); 
     Serial.print(" ");         
     Serial.print(needAdjustment);
     Serial.print(" ");
     Serial.print("magnetDirection:"); 
     Serial.print(" ");      
     Serial.print(magnetDirection);    
     Serial.println(" "); 
     */
stopCounter=0;
needAdjustment=0;
delay(100);
}


// ======================================== // 
int average (int readingPin,int numReadings)
{
int averagedValue=0;

for(int i=0; i < numReadings; i++) 
   {
   averagedValue = averagedValue + analogRead(readingPin);
   }
//averagedValue = averagedValue/numReadings;

//Serial.print(averagedValue);

return averagedValue;
}


// ======================================== // 
int decisionFunction(int  firstValue, int secondValue, int thirdValue)
{
int directionOfMagnet=0;

while(directionOfMagnet==0)
{
  if((firstValue>0) && (secondValue<0) && (thirdValue>0))
    {
    directionOfMagnet =1;
    }
  
    
  else if((firstValue>0) && (secondValue<0) && (thirdValue<0))
    {
     directionOfMagnet=2;
    }
  else if((firstValue>0) && (secondValue>0) && (thirdValue<0))
    {
     directionOfMagnet=10; // 10
    }
    
  else if((firstValue<0) && (secondValue>0) && (thirdValue<0))
    {
     directionOfMagnet=11; //11
    }
  else if((firstValue<0) && (secondValue>0) && (thirdValue>0))
    {
     directionOfMagnet=5; 
    }
  else if((firstValue<0) && (secondValue<0) && (thirdValue>0))
    {
     directionOfMagnet=6; 
    }
  
  else
    {
     directionOfMagnet=0;
      Serial.print("T'es serieux!!!");
       Serial.print(" ");
       Serial.print(firstValue);
       Serial.print(" ");
       Serial.print(secondValue);
       Serial.print(" ");
       Serial.print(thirdValue);
       Serial.println(" ");
     //delay(10000);
    }
  }    
return directionOfMagnet;
}

// ======================================== // 
void readPositionFunction()
{
int readPositionFunctionLoop=1;  

while(readPositionFunctionLoop==1)       
     {
     sensorValueA=average(sensorPinA,numReadings);
     sensorValueB=average(sensorPinB,numReadings);
     sensorValueC=average(sensorPinC,numReadings);

     decisionValueA=sensorValueB-sensorValueC;
     decisionValueB=sensorValueC-sensorValueA;
     decisionValueC=sensorValueA-sensorValueB;
     
     if((decisionValueA != 0) && (decisionValueB != 0) && (decisionValueC != 0))
       {
       readPositionFunctionLoop=0;
       }
     }
}

// ======================================== // 
void adjustPositionFunction(int positionOfTheServo, int previousPositionOfTheServo, int stepNumber)
{

if((previousPositionOfTheServo == 2) || ((previousPositionOfTheServo == 1)))  // counter-Clockwise rotation 
  {
  digitalWrite(dirPin, HIGH);
  }
else if((previousPositionOfTheServo == 5) || ((previousPositionOfTheServo == 6)))  // Clockwise rotation
  {
  digitalWrite(dirPin, LOW); 
  }

for (int i = 0; i < stepNumberForAdjustement-1; i++)
    {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(300); // Before 500
    digitalWrite(stepPin, LOW);
    //
    if(i>stepNumberForAdjustement-30)
    {
      readPositionFunction();
      magnetDirection=decisionFunction(decisionValueA,decisionValueB,decisionValueC); 
      if( (magnetDirection==1) || (magnetDirection==6) )
         {
         break;            
         }
    }
    else
    {
     delayMicroseconds(300); // Before 500 
     }
    
    }
  //delay(50);
}

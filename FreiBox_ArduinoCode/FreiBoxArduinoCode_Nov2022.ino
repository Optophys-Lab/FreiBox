// FreiBox code Nov 2022
// This code version includes:
// - Reward probability
// - Laser driving + masking LED
// 
// Overflow for micro = 71.6 minutes (2^32 / 1000000 / 60 = 71.6 minutes) => Reset button
#include <DIO2.h>
#include <Servo.h> 

//Input pins
const GPIO_pin_t ENTER_LICK_CHAMBER = DP31;
const GPIO_pin_t ENTER_NOSE_POKE = DP29;
const GPIO_pin_t LICK_RIGHT = DP3;
const GPIO_pin_t LICK_LEFT = DP2;

//Output pins
const int AUDITORY_CUE = 4; 
const GPIO_pin_t WATER_DELIVERY_RIGHT = DP51;
const GPIO_pin_t WATER_DELIVERY_LEFT = DP49;
const GPIO_pin_t LICK_CHAMBER_LIGHT = DP10; 
const GPIO_pin_t NOSE_POKE_PORT_LIGHT = DP11; 
const GPIO_pin_t LED3 = DP9; // Masking LED 
const GPIO_pin_t LED4 = DP8; // Not used, was 46
const GPIO_pin_t LASER_PIN = DP6;
const GPIO_pin_t MASKING_LED_TRIGGER = DP36;  // NEW
const GPIO_pin_t SYNC = DP7;
    
// For Servo
const byte interrupt_pin = 21;
const int servo_control_pin = 5;

// Imported Session parameters
int BLOCK_NUMBER = 0;
int BLOCK_LENGTH = 0;
int FIRST_BLOCK = 0; //Correct licking spout: 0=Right // 1= LEFT
int reward_prob = 0;
bool reward_bool = false; 

// Imported Epoch Duration
unsigned long ITI_DURATION;
unsigned long TIME_NOSEPOKE_TO_OPEN_GATE;
unsigned long WALKING_WINDOWS_DURATION;
unsigned long RESPONSE_WINDOWS_DURATION; 
unsigned long WAITING_ANTICIPATION; 
unsigned long POST_REWARD_WAITING;
unsigned long LASER_TIME; //1 = walking, 2 = response, 12 = walking and response, 3 = anticipation, 4 = post reward, 34 = anticipation and post reward
// Laser probability
long laser_random = 0;        //will be changed to a random number each trial
bool laser_on_bool = false;   //boolean if this trial will have a laser activation
int LASER_PROBABILITY;
int LASER_BLOCK;
int laser_this_block = 0;

// Imported 'Hardware' parameters
int number_licks_for_hit = 3;
int delay_between_licking_reading = 50; //in msec 
int pump_opening_time = 20; //in msec
int RESPONSE_CUE = 5000; // in Hz

// Behavioral results
int OMISSION = 0;
int HIT_LICKING = 0;
int MISS_LICKING = 0;
int ERROR_LICKING = 0;
int mouse_left_nose_poke_port = 0; // this will go 1 once mouse left nose poke port and we have saved that time stamp. after that we are no longer interested in nose poke port => To suppress (local only !!!)
unsigned long laser_on_time = 0;
unsigned long laser_off_time = 0;

//Max time: 70 min to avoid data and clock overflow
unsigned long max_time = 65 * 60 * 1000000; //up to 70 min in micro s
int max_block_length;

//Variable to check before each new trial whether we will hit the max time
unsigned long time_before_new_trial;

// Recording Arrays
const int lick_array_length = 100; //down from 100 = 5s max of recording with 50msec delay

// Exported licking array
unsigned long lick_array[lick_array_length];
unsigned long lick_array_Error[lick_array_length];
unsigned long lick_array_correct_spout_Anticipation[lick_array_length];
unsigned long lick_array_incorrect_spout_Anticipation[lick_array_length];
unsigned long lick_array_correct_spout_PostReward[lick_array_length];
unsigned long lick_array_incorrect_spout_PostReward[lick_array_length];

// Exported Head detection array
unsigned long chamber_leave_array_response_window[lick_array_length];
unsigned long chamber_leave_array_anticipation[lick_array_length];
unsigned long chamber_leave_array_post_reward[lick_array_length];

// exported Time variables to python
unsigned long session_start_time = 0;
unsigned long session_end_time = 0;
unsigned long light_on_time = 0;
unsigned long enter_nose_poke_port_time = 0;
unsigned long leave_nose_poke_port_time = 0;
unsigned long enter_lick_chamber_time = 0;
unsigned long omission_time = 0;
unsigned long auditory_cue_time = 0;
unsigned long error_time = 0;
unsigned long miss_time = 0;
unsigned long hit_time = 0; 
unsigned long reward_delivery_time = 0;
unsigned long trial_end = 0;
unsigned long python_transfer_start_time = 0;
unsigned long python_transfer_end_time = 0;

unsigned long gate_opening_time = 0; 

// exported Variables from Function

int licking_result_w_lick_number = 0;

//white noise
const int white_noise_values_number = 1000;
int rand_array[white_noise_values_number];

int licking_block_type = 0;
int licking_block_type_output = 0;

int time_out = 0;
int time_outDuration = 4000;

// Gate Control
Servo myServo; // create the servo object
int max_position_closing = 100; //Full counter-clockwise
int max_position_opening = 170; //Full clockwise
int servo_closing_speed = 50; // Delay in usec
int opening_stop = 0;
int emergency_opening = 0;

//Performance measure fo block changes
int OMISSION_WITHIN_BLOCK = 0;
int FILTERED_TRIAL_WITHIN_BLOCK_COUNTER = 0;
int TOTAL_TRIAL = 0;
int FIRST_TRIAL = 0;
int HIT_INTRA_BLOCK_COUNTER = 0;
int TOTAL_TRIAL_WITHIN_BLOCK_COUNTER = 0;
int finished_blocks = 0;
int moving_window_size = 20;
const int hit_array_total_size = 100;
int hit_array[hit_array_total_size];
float moving_average;
int current_index_hit_array = 0;
int change_block = 0;

//Parameters for training
int trainingStage=0;
int ignoreTheIncorrectSpout = 0; //To avoid TTL detection of removed spout (=incorrect)
int breakLickingDetection_Hit = 0; //For flexible licking response window
int breakLickingDetection_Error = 0; //For flexible licking response window
int trainingWithoutNosePoke = 0; // No Nose poking
int gate_closes_directly_after_error= 0; 

//Parameters for pulses signal encoding behavioral events (block type, trial outcome...) 
int interPulseInterval=200; // InterPulses interval in microsec

// ======================================== //   
void setup(){
// ======================================== //
memset(hit_array,-1,sizeof(hit_array));
// Fill array with 0
memset(lick_array,0,sizeof(lick_array));
memset(lick_array_Error, 0, sizeof(lick_array_Error));
memset(lick_array_correct_spout_Anticipation,0,sizeof(lick_array_correct_spout_Anticipation));
memset(lick_array_incorrect_spout_Anticipation,0,sizeof(lick_array_incorrect_spout_Anticipation));
memset(chamber_leave_array_anticipation,0,sizeof(chamber_leave_array_anticipation));
memset(chamber_leave_array_response_window,0,sizeof(chamber_leave_array_response_window));
memset(lick_array_correct_spout_PostReward,0,sizeof(lick_array_correct_spout_PostReward));
memset(lick_array_incorrect_spout_PostReward,0,sizeof(lick_array_incorrect_spout_PostReward));
memset(chamber_leave_array_post_reward,0,sizeof(chamber_leave_array_post_reward));

Serial.begin(38400);

//declare pins

pinMode(AUDITORY_CUE, OUTPUT);
pinMode2f(WATER_DELIVERY_RIGHT, OUTPUT);
pinMode2f(WATER_DELIVERY_LEFT, OUTPUT);
pinMode2f(NOSE_POKE_PORT_LIGHT, OUTPUT);
pinMode2f(LICK_CHAMBER_LIGHT, OUTPUT);
pinMode2f(LED3, OUTPUT);
pinMode2f(LED4, OUTPUT);
pinMode2f(LASER_PIN, OUTPUT);
pinMode2f(SYNC, OUTPUT);
pinMode2f(MASKING_LED_TRIGGER, OUTPUT);  // NEW
pinMode2f(ENTER_LICK_CHAMBER, INPUT_PULLUP);
pinMode2f(ENTER_NOSE_POKE, INPUT_PULLUP);
pinMode2f(LICK_RIGHT, INPUT_PULLUP);
pinMode2f(LICK_LEFT, INPUT_PULLUP);
digitalWrite2f(LICK_CHAMBER_LIGHT, LOW);
digitalWrite2f(NOSE_POKE_PORT_LIGHT, LOW);
digitalWrite2f(LED3, LOW);
digitalWrite2f(LED4, LOW);
digitalWrite2f(SYNC, LOW);
digitalWrite2f(LASER_PIN, LOW);
digitalWrite2f(MASKING_LED_TRIGGER, LOW);  // NEW

make_frequencies_for_white_noise(white_noise_values_number);


// For Servo gate
myServo.attach(servo_control_pin);
pinMode(interrupt_pin, INPUT_PULLUP);
attachInterrupt(digitalPinToInterrupt(interrupt_pin), open_gate, CHANGE);
close_gate(servo_closing_speed); // close gate completely at beginning

randomSeed(analogRead(A0));

}

// ======================================== //
void loop()
{
// ======================================== // 
// Think about catch trials (same protocol without Cue)
while(FIRST_TRIAL == 0) // things we only need to do once, at the very beginning of a session    
     {  
     FIRST_TRIAL++; // Increment by 1 TOTAL_TRIAL to avoid infinite loop
     define_python_variables(); // get parameters from python GUI    
     max_block_length = BLOCK_LENGTH * 5; // To avoid infinite block length (important if an optogenetic effect occurs)    
     close_gate(servo_closing_speed); // close gate completely at beginning    
     session_start_time = micros();    
     pulses_signal(SYNC,10, 1); //Session start          
     
     if(trainingStage > 0)
       {
       defineTrainingParameters(trainingStage);
       }   
    
     licking_block_type = FIRST_BLOCK; // determine which spout is correct in this first block
     //licking_block_type_output = licking_block_type; //for debugging
     // determine if first block will be laser block
     if((LASER_BLOCK == 1) ||(LASER_BLOCK==12)||(LASER_BLOCK==123)||(LASER_BLOCK==1234))
       {
       laser_this_block = 1;
       }
     }     

// 0. Trial preparation: check if we still need more trials (block number and max ssssion time)
while((finished_blocks < BLOCK_NUMBER) && (time_before_new_trial < max_time))   
     { 
      // Resetting of all exported variables
      reset_exported_variables();
      // Pulses for recordings
      pulses_licking_block(licking_block_type); //Trial start         
    //A: Laser probability - for each trial, generate a random number (laser_random) which define if the laser is ON or OFF during the trial (laser_on_bool)
      laser_random = random(100);// make a random number that determines if we use laser this trial or not (in case that it is random)
      if(laser_random >= 100-LASER_PROBABILITY) //randomly choosing if the trial was a laser trial or not
        {      
        laser_on_bool = true;
        }
      else
        { 
        laser_on_bool = false;
        }
      //B: Reward probability  /////// NEW ////////////
     int  reward_random = random(100);
      if(reward_random <= reward_prob)
        {      
        reward_bool = true;
        }
      else
        { 
        reward_bool = false;
        }
      

// 1. ITI and Gate opening
 
      ITI_function(ITI_DURATION); // ITI
      
      // if mouse has nose in nose poke port before trial start, this waits until it comes out of port
      wait_for_no_beam_breaking_nose_poke_port(50);      
      
// 2. Nose poke port available - light ON
      light_on_time = (millis()- (session_start_time/1000))*1000;

      if (trainingWithoutNosePoke==0)                               // If condition for training (Without nose poke)
         {
         digitalWrite2f(NOSE_POKE_PORT_LIGHT, HIGH);
         digitalWrite2f(SYNC, HIGH);    // Synchronization pin: Light On
         digitalWrite2f(LED3, HIGH);  /// Changed on 09/03/22
         }          

     
      if(LASER_TIME == 5)  // turn on laser, if walking is desired stimulation period
        {
        unsigned long startWaitingPeriod = micros()- session_start_time;
        unsigned long currentIime = micros() - session_start_time;  //initialize for current "time" and update at the end of each iteration
        int leave_nose_poke_port = 0; // to check when mouse left nose poke port with debouncing
        int nosePokeDone = 0;
        while(currentIime - startWaitingPeriod < 1000000)  //test whether the period has elapsed
             {
             if(digitalRead2f(ENTER_NOSE_POKE) == LOW) // 3. Read ENTER_NOSE_POKE until mice enter the nose poke port
               { 
               currentIime = micros()- session_start_time; // update current time in waiting period
               }
  
             else
               {
               nosePokeDone = 1;
               laser_on_bool = false;
               break;
               }
             }
        
        if((laser_this_block > 0) && (laser_on_bool))
          {      
          turn_laser_on();        // NEW        
          }
          masking_LED_on(MASKING_LED_TRIGGER);                
        
        if((trainingWithoutNosePoke==0)&(nosePokeDone==0))                         // If condition for training (Without nose poke)
           {
           while(digitalRead2f(ENTER_NOSE_POKE) == LOW)              
                {
                //Serial.println("I'm still waiting for Head entry");
                }
           }  
        
        }
        
      else
        {
        // 3. Read ENTER_NOSE_POKE until mice enter the nose poke port
        if (trainingWithoutNosePoke==0)                               // If condition for training (Without nose poke)
           {
           while(digitalRead2f(ENTER_NOSE_POKE) == LOW)              
                {
                //Serial.println("I'm still waiting for Head entry");
                }
           }         
        }
    
//Optional 4.5. Turn on laser  if Walking period is desired stimulation period  
      if((LASER_TIME == 1 )||(LASER_TIME == 12)||(LASER_TIME == 123)||(LASER_TIME == 1234))  // turn on laser, if walking is desired stimulation period
              {
              if((laser_this_block > 0) && (laser_on_bool))
                {      
                  turn_laser_on();        // NEW        
                }
                masking_LED_on(MASKING_LED_TRIGGER); 
              }         
      
      // Once they entered the nose poke port, check again if there is still time left because this might take a while depending on animals' motivation (max time might have been reached)
      time_before_new_trial = micros()- session_start_time;     
      if(time_before_new_trial < max_time)
        {   
        enter_nose_poke_port_time = micros()- session_start_time; // save time of nose poke       
        TOTAL_TRIAL++;
        TOTAL_TRIAL_WITHIN_BLOCK_COUNTER++;  
       
// 4. Waiting epoch before gate is opened. Register when the mouse leaves the nose poke port         
        if (trainingWithoutNosePoke==0)                                                                
           {
             digitalWrite2f(SYNC, LOW); // Synchronization pin: Nose Poke 
             digitalWrite2f(LED3, LOW);  /// Changed on 09/03/22   
           waiting_debouncing_function(ENTER_NOSE_POKE, TIME_NOSEPOKE_TO_OPEN_GATE, 50);                                    
          
           digitalWrite2f(NOSE_POKE_PORT_LIGHT, LOW); // signal nose poke port no longer available        

           }
                                                                                                        
//5. Open Gate
        digitalWrite2f(LICK_CHAMBER_LIGHT, HIGH); 
        open_gate(); // gate open = mouse can enter lick chamber    
      
             
//6. Walking to LCC / wait for head entry in lick chamber
        wait_for_entering_lick_chamber_fct(WALKING_WINDOWS_DURATION, 50); // test whether the walking time period has elapsed return ()
                                                                        // RETURN leave_nose_poke_port_time and enter_lick_chamber_time   
                                                                        // Set SYNC pin to LOW and HIGH when animal leaves the nose poke and enters in licking chamber respectively
//6.5 Laser OFF after Head Entry        
        if((LASER_TIME == 1) && (laser_this_block > 0) && (laser_on_bool))
          { 
              turn_laser_off();        // NEW             
          }

//OMISSION / mouse did not enter lick chamber
        if(enter_lick_chamber_time == 0)      
          {
          OMISSION++;
          OMISSION_WITHIN_BLOCK++;
          omission_time = micros()- session_start_time;
          // LASER
          // turning off because in case of omission, this ends the trial          
          turn_laser_off();        // NEW             
           
          pulses_signal(SYNC,4, 0);
           present_white_noise(white_noise_values_number); //white noise punishment  
          time_out = 1;
          } 
       
// if mouse entered lick chamber 
        else if(enter_lick_chamber_time > 0)  
          {    
            // LASER    
          if((LASER_TIME == 2)||(LASER_TIME == 23)||(LASER_TIME == 234) ) // turn on laser, if response window is desired stimulation period
           {
                 masking_LED_on(MASKING_LED_TRIGGER);
                 if((laser_this_block > 0)&& (laser_on_bool))
                 {              
                 turn_laser_on();        // NEW      
                }
           }
          
        
// 7. Licking response  
          licking_result_w_lick_number = Record_lick_head_detection_during_waiting_epoch(RESPONSE_WINDOWS_DURATION,licking_block_type,delay_between_licking_reading,lick_array,lick_array_Error,chamber_leave_array_response_window, 1);
                      // RETURN >0: the number of licks for correct licking on rewarded spout / -1: if licking only on unrewarded spout / -2: for licking on both unrewarded and rewarded spout / 0: else      
                  
          // Laser OFF after Licking response  
          if ((laser_this_block > 0)&& (laser_on_bool)){
                  if((LASER_TIME == 2) ||(LASER_TIME == 12))
                    { 
                    turn_laser_off();        // NEW      
                    }   
          }
           FILTERED_TRIAL_WITHIN_BLOCK_COUNTER++; 

//MISS = not enough or no licks       
          if((licking_result_w_lick_number < number_licks_for_hit) && (licking_result_w_lick_number >= 0)) 
            {
            MISS_LICKING++;
            miss_time = micros()- session_start_time;
            if (reward_bool) // Miss (Unrewarded)   
               {                                    
                pulses_signal(SYNC,6, 0);               
               }                                    
            else // Rewarded Miss
               {
                pulses_signal(SYNC,12, 0);
               }
            time_out = 1;
            hit_array[current_index_hit_array] = 0;
            current_index_hit_array++;
            present_white_noise(white_noise_values_number); //white noise punishment   

           if (gate_closes_directly_after_error==0){
             
                // Anticipation period just like for hits
                // includes laser
                      reward_anticipation_period(WAITING_ANTICIPATION, licking_block_type, delay_between_licking_reading,
                       lick_array_correct_spout_Anticipation, lick_array_incorrect_spout_Anticipation, chamber_leave_array_anticipation, 0);
                // post-miss reward with GUI-probability
                if (!reward_bool){
                 // Reward after error
                  reward_delivery();  
                    }
                digitalWrite2f(SYNC, LOW);
                digitalWrite2f(LED3, LOW);  /// Changed on 09/03/22    
                // post reward for errors
                 post_reward_period(); // includes laser
                }   
            }
 
//ERROR = Licking on the wrong spout - negative value
          else if(licking_result_w_lick_number < 0) // 
            {
            ERROR_LICKING++;
            error_time = micros()-session_start_time;
            if (reward_bool) // Error (Unrewarded)   
               {                                    
                pulses_signal(SYNC,5, 0);               
               }                                    
            else  // Rewarded Error
               {
                pulses_signal(SYNC,11, 0);
               }
            
            time_out = 1;
            hit_array[current_index_hit_array] = 0;
            current_index_hit_array++;
            // white noise
            present_white_noise(white_noise_values_number); //white noise punishment 
            
             if (gate_closes_directly_after_error==0)
             {               
                   // Anticipation period just like for hits
                   // includes laser
                      reward_anticipation_period(WAITING_ANTICIPATION, licking_block_type, delay_between_licking_reading,
                       lick_array_correct_spout_Anticipation, lick_array_incorrect_spout_Anticipation, chamber_leave_array_anticipation, 0);
                     
                        
                  // post-error reward with GUI-probability
                  if (!reward_bool)
                  {                      
                   // Reward after error
                    reward_delivery();  
                      }
                  digitalWrite2f(SYNC, LOW);
                  digitalWrite2f(LED3, LOW);  /// Changed on 09/03/22    
                  // post reward for errors
                   post_reward_period(); // includes laser
              }
                                    
            }     

//HIT = licking on the correct spout (positive value) AND sufficiently many licks            
        else if(licking_result_w_lick_number >= number_licks_for_hit)
            {
            hit_time = micros()- session_start_time;
            if (reward_bool) // Hit (Rewarded)   ////////////////////////////////////////////////////////////////////////////////////////////////////
               {                                    ////////////////////////////////////////////////////////////////////////////////////////////////////
                pulses_signal(SYNC,7, 0);           ////////////////////////////////////////////////////////////////////////////////////////////////////     
               }                                    ////////////////////////////////////////////////////////////////////////////////////////////////////
            else  // Unrewarded Hit
               {
                pulses_signal(SYNC,13, 0);
               }            
             
            HIT_LICKING++;    
            HIT_INTRA_BLOCK_COUNTER++;
            hit_array[current_index_hit_array] = 1;
            current_index_hit_array++;
            
//8. Auditory Cue  
        auditory_cue_time = micros()- session_start_time; // save time stamp 
        tone(AUDITORY_CUE, RESPONSE_CUE);
        delay(70);
        noTone(AUDITORY_CUE);

// 9. Waiting epoch before Reward delivery
     // this includes laser           
            reward_anticipation_period(WAITING_ANTICIPATION, licking_block_type, delay_between_licking_reading,
                       lick_array_correct_spout_Anticipation, lick_array_incorrect_spout_Anticipation, chamber_leave_array_anticipation, 0);
            
//10. REWARD DELIVERY on the correct spout, depending on block type
    if (reward_bool)
    {
      reward_delivery();      
        }
     digitalWrite2f(SYNC, LOW); 
     digitalWrite2f(LED3, LOW);  /// Changed on 09/03/22    
                               
// 11. Post reward epoch to record licking and Head Entry          
          post_reward_period(); // includes laser
          }                               
           digitalWrite2f(SYNC, HIGH);
           digitalWrite2f(LED3, HIGH);  /// Changed on 09/03/22
// end if/else for entering lick chamber during response window        
          }   
                  
// 12. Lights OFF
        digitalWrite2f(LICK_CHAMBER_LIGHT, LOW);

// 13. Closing the gate
        close_gate(servo_closing_speed);
       
       
// 14. time Out      
        if(time_out == 1)
          {
          delay(time_outDuration);
           
          }    
// 15. Data transfer
        trial_end = micros()- session_start_time;
        pulses_signal(SYNC,8, 0); 
        python_transfer_start_time = micros() - session_start_time;
        data_transfer();        
                 
// 16. Block Changes 
    check_for_new_block();   
                
      // take time at end of trial to see if time limit of session has been reached
      time_before_new_trial = micros() - session_start_time;    
      }
        // if time limit reached, end session
      else
        {       
       
        }
     }
     
   end_session();
} //END

// ======================================== // 
 void masking_LED_on(const GPIO_pin_t MASKING_LED){
  digitalWrite2f(MASKING_LED, HIGH);  // NEW 
 delayMicroseconds(200); // NEW    
    digitalWrite2f(MASKING_LED, LOW);  // NEW           
 }

// ======================================== // 
 void turn_laser_on(){
// ======================================== // 
          
    digitalWrite2f(LASER_PIN, HIGH);          
    laser_on_time = micros() - session_start_time;
    delayMicroseconds(500); 
    digitalWrite2f(LASER_PIN, LOW);    
 }

// ======================================== // 
void turn_laser_off(){
// ======================================== //      
    digitalWrite2f(LASER_PIN, LOW);         
    laser_off_time = micros() - session_start_time; 
}
          
// ======================================== // 
void check_for_new_block(){
// ======================================== // 
   // SAFETY: if max number of trials in a block is surpassed, stop using laser, and stop session     
        if(FILTERED_TRIAL_WITHIN_BLOCK_COUNTER >= max_block_length)
          {
          laser_this_block = 0;
          end_session();
          }
  // 1. Check if we have enough trials for the moving window
 
  if((FILTERED_TRIAL_WITHIN_BLOCK_COUNTER >= moving_window_size) && (omission_time == 0))
        {        
        // compute average across the window
        average_across_array();
        
        // if performance exceeds criterion in this window - new block
        if(moving_average >= 0.75)  //NEW
          {
          change_block = 1;
          }
          // if performance below criterion, keep window going
        else
          {
          change_block = 0;
          }
       if (omission_time == 0){
          // get rid of first array value and shift all other values 1 index down
          update_array_for_moving_window();  
        }     
        
        // BLOCK CHANGE after sufficiently many correct trials (75%) in sliding window & desired block length
        if((change_block > 0) && (FILTERED_TRIAL_WITHIN_BLOCK_COUNTER >= BLOCK_LENGTH))
          {
              reset_variables_for_new_block();
              // update correct side in this new block         
              licking_block_type = licking_block_type*(-1); 
              // determine if next block will be laser block
              if((LASER_BLOCK == finished_blocks + 1)||(LASER_BLOCK==123))
                {
                laser_this_block = 1;
                }
               else
                {
                laser_this_block = 0;
                }
          } 
        }
 }


// ======================================== // 
void update_array_for_moving_window(){
// ======================================== // 
      // get rid of first array value and shift all other values 1 index down
      for(int i = 0; i < moving_window_size - 1; i++)
         {
         hit_array[i] = hit_array[i+1];
         }
     // adjust index so next value will go in the last slot of array
      current_index_hit_array = moving_window_size - 1;

}

// ======================================== // 
void average_across_array(){
// ======================================== // 
  long sum = 0L ;  // sum will be larger than an item, long for safety.
  for (int t = 0 ; t < moving_window_size ; t++)
    sum += hit_array[t] ;
  moving_average = ((float) sum) / moving_window_size ;  
}


// ======================================== // 
void reset_variables_for_new_block(){
// ======================================== // 
    FILTERED_TRIAL_WITHIN_BLOCK_COUNTER = 0;
    HIT_INTRA_BLOCK_COUNTER = 0;
    TOTAL_TRIAL_WITHIN_BLOCK_COUNTER = 0;
    OMISSION_WITHIN_BLOCK = 0;
    finished_blocks++;
    change_block = 0;
    memset(hit_array,-1,sizeof(hit_array));        
    current_index_hit_array = 0;
}

// ======================================== // 
void wait_for_no_beam_breaking_nose_poke_port(int delay_debouncing){ // checks if mouse has nose in nose poke port before trial start
// ======================================== // 
while(digitalRead2f(ENTER_NOSE_POKE)==HIGH) // stuck in this loop until it takes out nose
     {
     //Serial.println("get out");
     }
delay(delay_debouncing);
while(digitalRead2f(ENTER_NOSE_POKE)==HIGH) // repeat after short delay to be sure mouse is out of port (debouncing)    
     { 
     // Serial.println("get out2");
     }
}

// ======================================== // 
void wait_for_no_beam_breaking_lick(int delay_debouncing){
// ======================================== // 
// checks if mouse has nose in nose poke port before trial start
// stuck in this loop until it takes out nose
while (digitalRead2f(ENTER_LICK_CHAMBER)==HIGH)
      {
      // Just wait for animal to leave
    
      }
      delay(delay_debouncing);
// repeat after short delay to be sure mouse is out of port (debouncing)      
while (digitalRead2f(ENTER_LICK_CHAMBER)==HIGH)
      {
      // Just wait for animal to leave  
      }
}
 
// ======================================== // 
void reset_exported_variables(){
// ======================================== // 
time_out = 0;
  
// exported Time variables to python
light_on_time = 0;
enter_nose_poke_port_time = 0;
leave_nose_poke_port_time = 0;
licking_result_w_lick_number = 0; 
omission_time = 0;
enter_lick_chamber_time = 0;

auditory_cue_time = 0;
error_time = 0;
miss_time = 0;
hit_time = 0; // Also Hit Time
reward_delivery_time = 0;
trial_end = 0;
python_transfer_start_time = 0;
python_transfer_end_time = 0;
laser_on_time = 0;
laser_off_time = 0;

// exported Variables from Function

memset(lick_array, 0, sizeof(lick_array));
memset(lick_array_Error, 0, sizeof(lick_array_Error));
memset(lick_array_correct_spout_Anticipation, 0, sizeof(lick_array_correct_spout_Anticipation));
memset(lick_array_incorrect_spout_Anticipation, 0, sizeof(lick_array_incorrect_spout_Anticipation));
memset(lick_array_correct_spout_PostReward, 0, sizeof(lick_array_correct_spout_PostReward));
memset(lick_array_incorrect_spout_PostReward, 0, sizeof(lick_array_incorrect_spout_PostReward));
memset(chamber_leave_array_anticipation, 0, sizeof(chamber_leave_array_anticipation));
memset(chamber_leave_array_post_reward, 0, sizeof(chamber_leave_array_post_reward));
memset(chamber_leave_array_response_window, 0, sizeof(chamber_leave_array_response_window));
}

// ======================================== // 
void pulses_licking_block(int BlockType){
// ======================================== // 
switch(BlockType) //Correct licking spout: -1=Right // 1= LEFT
      { 
      case -1:
            { 
            delayMicroseconds(500);  
            for(int iteration = 0; iteration < 2; iteration++)
            {    
            digitalWrite2f(SYNC,HIGH);
            delayMicroseconds(interPulseInterval);
            digitalWrite2f(SYNC,LOW);
            delayMicroseconds(interPulseInterval); 
            }
            break;
            }
      case 1:
            {
            for(int iteration = 0; iteration < 3; iteration++)
            {
            digitalWrite2f(SYNC,HIGH);
            delayMicroseconds(interPulseInterval);
            digitalWrite2f(SYNC,LOW);
            delayMicroseconds(interPulseInterval);
            }
            break;
            }
      }
       delayMicroseconds(500);  
}

// ======================================== // 
void pulses_signal(const GPIO_pin_t syncPin, int goal_iteration, bool end_or_within){
// ======================================== // 
digitalWrite2f(syncPin,LOW);
delayMicroseconds(500);
for(int iteration = 0; iteration < goal_iteration; iteration++)
   {
   digitalWrite2f(syncPin,HIGH);
   delayMicroseconds(interPulseInterval);
   digitalWrite2f(syncPin,LOW);
   delayMicroseconds(interPulseInterval);    
   }
if(end_or_within >0)
  {
  delayMicroseconds(500);
  }
delayMicroseconds(500);   
}

// ======================================== // 
void ITI_function(unsigned long ITI_duration_in_usec){
// ======================================== //   
unsigned long start_ITI_period = micros()- session_start_time;  //start time of waiting period
unsigned long current_time_in_ITI_period = micros()- session_start_time;  //initialize for current "time" and update at the end of each iteration

while(current_time_in_ITI_period - start_ITI_period < ITI_duration_in_usec)  //test whether the period has elapsed
     {
     current_time_in_ITI_period = micros()- session_start_time;
     }
}

// ======================================== //
void open_gate(){
// ======================================== // 
myServo.write(max_position_opening);
}

// ======================================== // 
void close_gate(int closing_speed){
// ======================================== // 

for(int position_servo = max_position_opening; position_servo > max_position_closing; position_servo--)
   {
   if(position_servo <= (max_position_opening-20))
     {
     if(digitalRead2f(ENTER_LICK_CHAMBER) == HIGH) 
       {
       myServo.write(max_position_opening-25);           
       position_servo =  max_position_opening-25;
       delay(50);
       }
     } 
   myServo.write(position_servo);     
   delay(closing_speed);
   }   
}


// ======================================== //   
int waiting_debouncing_function(const GPIO_pin_t pinToRead, unsigned long time_between_two_events, int delay_debouncing){  //debouncing = check for 2 consecutive time points where nose poke port is empty
// ======================================== //  
unsigned long start_waiting_period = micros()- session_start_time;
unsigned long current_time_in_waiting_period = micros() - session_start_time;  //initialize for current "time" and update at the end of each iteration
int leave_nose_poke_port = 0; // to check when mouse left nose poke port with debouncing
while(current_time_in_waiting_period - start_waiting_period < time_between_two_events)  //test whether the period has elapsed
     {
     // if the mouse has not already left the nose poke port before, this here identifies the time stamp when it did
     if(leave_nose_poke_port_time == 0)
       {
       if(digitalRead2f(pinToRead) == LOW) 
         {
         leave_nose_poke_port++;
         delay(delay_debouncing); // debounce and check twice
         if(digitalRead2f(pinToRead) == LOW) 
           {
           leave_nose_poke_port_time = micros() - session_start_time; // save that time stamp after debouncing
           digitalWrite2f(SYNC, HIGH);   /////////////////////////////////////////////////////////////////////<<<<<<<<<<<<<<<<<<<<<<<<<< Modification Brice 07/12/20          
           digitalWrite2f(LED3, HIGH);  /// Changed on 09/03/22
           mouse_left_nose_poke_port = 1;   
           }
         else
           {
           leave_nose_poke_port = 0;
           }
         }    
       }
       // if the mouse has not already left the nose poke port before, we just wait until the time window has passed
       else
         {}
       current_time_in_waiting_period = micros()- session_start_time; // update current time in waiting period      
       }
}

// ======================================== //   
int wait_for_entering_lick_chamber_fct(unsigned long window_duration, int delay_debouncing){ //test whether the walking time period has elapsed 
// ======================================== //  RETURN: entry_lick_chamber;   
 // we break out of this function as soon as the mouse enters lick chamber
int leave_nose_poke_port = 0; // to check when mouse left nose poke port with debouncing
int entry_lick_chamber;
unsigned long start_window = micros()- session_start_time;  //start time of lick detection
unsigned long current_time = micros()- session_start_time;  //initialize for current "time" and update at the end of each iteration

if (trainingWithoutNosePoke==1)
   {
   leave_nose_poke_port_time = 0;
   current_time = start_window;
   window_duration=1000000;
   }
   
while(current_time - start_window < window_duration)
     {
     //1. if no timestamp for leaving NPP yet, keep looking
     if(leave_nose_poke_port_time == 0)
       {
       if(digitalRead2f(ENTER_NOSE_POKE) == LOW) 
         {
         leave_nose_poke_port++;
         delay(delay_debouncing); // debounce and check twice
         if(digitalRead2f(ENTER_NOSE_POKE) == LOW) 
           {

           leave_nose_poke_port_time = micros() - session_start_time; // save that time stamp after debouncing
           digitalWrite2f(SYNC, HIGH);
           digitalWrite2f(LED3, HIGH); 
           mouse_left_nose_poke_port = 1;
           }
         else
           {
           leave_nose_poke_port = 0;
           }
         }
      }
     else
       {}
     //2. check when the mouse enters the lick chamber      
     if(digitalRead2f(ENTER_LICK_CHAMBER) == HIGH)
       {
       enter_lick_chamber_time = micros() - session_start_time; 
       digitalWrite2f(SYNC, LOW);
       digitalWrite2f(LED3, LOW);
      // entry_lick_chamber = 1; 
       break;     // we break out of this function as soon as the mouse enters lick chamber
       }
      
     if(enter_lick_chamber_time > 0)
       {
       break; 
       }
     if(trainingWithoutNosePoke==0)
       {  
       current_time = micros()- session_start_time; 
       }
     }
}

// ======================================== //   
int Record_lick_head_detection_during_waiting_epoch(unsigned long waitingTimeInMicroSec,int BlockType,int reading_delay,unsigned long lick_array_correct_spout[], unsigned long lick_array_incorrect_spout[], unsigned long chamber_leave_array[], int response_window){
// ======================================== // 

unsigned long start_waiting = micros()- session_start_time; 
int all_licks_correct_spout = 0; // count
int all_licks_incorrectSpout = 0; // count

int lick_index_CorrectSpout = 0;  // position in array, i.e. for several events in 1 trial, they are all filled consecutively into array
int lick_index_incorrectSpout = 0;  // position in array, i.e. for several events in 1 trial, they are all filled consecutively into array

int lick_index_Error = 0;
int all_licks_Error = 0;
int all_licks = 0; // positive values here correspond to correct licks in a trial, negative values to error licks

int chamber_leave = 0; // count
int chamber_leave_index = 0; // position in array, i.e. for several events in 1 trial, they are all filled consecutively into array
unsigned long new_time = 0; // this will be incremented to keep track of how much time has passed
unsigned long current_time_in_waiting_period = micros() - session_start_time;  //initialize for current "time" and update at the end of each iteration
int skip_reading_delay = 0;
int  hit_or_error_signaled = 0;

while (current_time_in_waiting_period - start_waiting < waitingTimeInMicroSec)  //test whether the period has elapsed
      {      
      switch(BlockType) //Correct licking spout: -1 = Right // 1 = LEFT
            { 
             // Right = Correct
            case -1:
                   {
                    if (digitalRead2f(LICK_RIGHT) == LOW) // Licking on the RIGHT spout = HIT
                       { 
                       all_licks_correct_spout++;
                       //count lick time stamps
                       new_time = micros() - session_start_time; // time stamp to fill into lick array  
                       lick_array_correct_spout[lick_index_CorrectSpout] = new_time; //fill array of correct licks
                       lick_index_CorrectSpout++; // update current position in array

                       if(lick_index_CorrectSpout <= number_licks_for_hit)
                         {
                          pulses_signal(SYNC,1, 1);
                         }
                       
                       if (lick_index_CorrectSpout >= lick_array_length)
                          {
                            lick_index_CorrectSpout = 0;
                          }
                       }

                    else if (digitalRead2f(LICK_LEFT)==LOW) // Licking on the LEFT spout = ERROR
                       { 
                        
                       all_licks_incorrectSpout++;                      
                       //count lick time stamps
                       new_time = micros() - session_start_time; // time stamp to fill into lick array   
                       lick_array_incorrect_spout[lick_index_incorrectSpout] = new_time; //fill array of incorrect licks
                       lick_index_incorrectSpout++; // update current position in array

                       if(lick_index_incorrectSpout==1)
                         {
                          pulses_signal(SYNC,1, 1);
                         }
                       
                       
                       if (lick_index_incorrectSpout >= lick_array_length)
                          {
                            lick_index_incorrectSpout = 0;
                          }
                       if  (ignoreTheIncorrectSpout == 0)
                          {
                          break;
                          }
                                                
                       }
                   
                    else if (digitalRead2f(ENTER_LICK_CHAMBER)==LOW) // leave lick chamber = ERROR
                       { 
                       chamber_leave++;
                       //count lick time stamps
                       new_time = micros() - session_start_time;   // time stamp to fill into chamber leave array 
                       chamber_leave_array[chamber_leave_index] = new_time; //fill array of chamber leaves
                       chamber_leave_index++; // update current position in array                        
                       if (chamber_leave_index >= lick_array_length)
                          {
                            chamber_leave_index = 0;
                          }
                       }                   
                   break;
                   }
             
            case 1:  // Left = Correct
                   { 
                    if (digitalRead2f(LICK_LEFT)==LOW) // Licking on the LEFT spout = HIT
                       { 
                       all_licks_correct_spout++;
                       //count lick time stamps
                       new_time = micros() - session_start_time;   // time stamp to fill into lick array  
                       lick_array_correct_spout[lick_index_CorrectSpout] = new_time;  //fill array of correct licks
                       lick_index_CorrectSpout++;// update current position in array 

                       if(lick_index_CorrectSpout <= number_licks_for_hit)
                         {
                          pulses_signal(SYNC,1, 1);
                         }
                       
                       if (lick_index_CorrectSpout >= lick_array_length)
                          {
                            lick_index_CorrectSpout = 0;
                          }
                       }

                   else if (digitalRead2f(LICK_RIGHT)==LOW) // Licking on the RIGHT spout = ERROR
                       { 
                       all_licks_incorrectSpout++;                       
                       //count lick time stamps
                       new_time = micros() - session_start_time;   // time stamp to fill into lick array  
                       lick_array_incorrect_spout[lick_index_incorrectSpout] = new_time;  //fill array of incorrect licks
                       lick_index_incorrectSpout++;  // update current position in array  

                       if(lick_index_incorrectSpout==1)
                         {
                          pulses_signal(SYNC,1, 1);
                         }
                                              
                       if (lick_index_incorrectSpout >= lick_array_length)
                          {
                            lick_index_incorrectSpout = 0;
                          }
                       if (ignoreTheIncorrectSpout == 0)
                          {
                          break;
                          } 
                       }
                       
                    else if (digitalRead2f(ENTER_LICK_CHAMBER)==LOW) //leave lick chamber t = ERROR
                       { 
                       chamber_leave++;
                       //count lick time stamps
                       new_time = micros() - session_start_time; // time stamp to fill into chamber leave array    
                       chamber_leave_array[chamber_leave_index] = new_time;  //fill array of chamber leaves
                       chamber_leave_index++;// update current position in array 
                       if (chamber_leave_index >= lick_array_length)
                          {
                            chamber_leave_index = 0;
                          }
                       }   
                   break;
                   }            
            }    
      
      // special conditions, depending on training stage
    
      if((breakLickingDetection_Hit == 1) && (all_licks_correct_spout >= number_licks_for_hit) && ( response_window > 0))  // in case of correct licks, break out
        {   
          break;          
        }       
      if((breakLickingDetection_Error == 1) && (all_licks_incorrectSpout>0) && ( response_window > 0))  // in case of error licks, break out in stage 5
        {   
          break;          
        }    
        //if (skip_reading_delay > 0){   
      // predetermined delay between readings to avoid data overflow
      delay(reading_delay); 
       // skip_reading_delay = 0;
       //}
       
      current_time_in_waiting_period = micros()- session_start_time; 
      }
      
// To ignore TTL from spout removed during the training  
if (ignoreTheIncorrectSpout == 1)      
   {
   all_licks_incorrectSpout = 0; 
   }
//  


if ((all_licks_incorrectSpout > 0) && (all_licks_correct_spout > 0))
   {
   all_licks = -2;  
   }
else if ((all_licks_incorrectSpout <= 0) && (all_licks_correct_spout > 0))
   {
   all_licks = all_licks_correct_spout;  
   }
else if (all_licks_incorrectSpout > 0)
   {
   all_licks = - 1; // Error = -1 
   }

/*else
   {
   all_licks = 0;  
   }*/  
  
return all_licks; // -1: Only incorrect licking / -2: both incorrect and correct licking / > 0 else
}
// ======================================== //
void present_white_noise(const int random_values_needed){
// ======================================== //
unsigned long noise_start_time = micros();
unsigned long current_time = micros();
int index_in_array=1;

//present white noise for 50 ms
while (current_time - noise_start_time < 150000 )
      {
      if(index_in_array < random_values_needed - 1)
        {
        digitalWrite(AUDITORY_CUE, HIGH);
        delayMicroseconds(rand_array[index_in_array]);
        digitalWrite(AUDITORY_CUE, LOW);
        index_in_array++;
        delayMicroseconds(rand_array[index_in_array]);
        index_in_array++;
        current_time = micros();
        }        
      //if at the end of the array, start from beginning again
      else
        {
        index_in_array = 1;
        }
      }
}

// ======================================== //
void make_frequencies_for_white_noise(const int random_values_needed){
// ======================================== //
unsigned long rand_long;
int rand_int_micros;
for(int p=0; p < random_values_needed; p++)
   {
   rand_long = random(0, 1023);
   // random values for frequencies in between 1 and 20 kHz  
   rand_int_micros = my_map(rand_long, 0, 1023, 1, 20);
   //transfer these frequencies into micro s delay
   rand_array[p] = (1.0 / rand_int_micros) * 1000;
   //Serial.println(rand_array[p]);  
   }
}

// ======================================== //
float my_map(float x, float in_min, float in_max, float out_min, float out_max){
// ======================================== //
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}


// ======================================== //
void initiate_reward(const GPIO_pin_t rewardDeliveryPin, int openingTime){
// ======================================== //
digitalWrite2f(rewardDeliveryPin,HIGH); 
delay(openingTime);
digitalWrite2f(rewardDeliveryPin,LOW);
}

// ======================================== //
void print_array(unsigned long arrayToPrint[], int arrayLength){
// ======================================== //
for(int k = 0; k < arrayLength; k++)
   {
   Serial.print(arrayToPrint[k]);
   if(k < (arrayLength - 1))
     {
     Serial.print(";");
     }
   else
     {   
     }
   }
}


// ======================================== //
void reward_delivery(){
// ======================================== //
       reward_delivery_time = micros() - session_start_time;
          switch(licking_block_type) //Correct licking spout: -1 = Right // 1 = LEFT
                { 
                case -1: // right correct
                       {
                        
                       initiate_reward(WATER_DELIVERY_RIGHT,pump_opening_time);
                       break;
                       }    
                                            
                case 1: // left correct     
                       {
                       initiate_reward(WATER_DELIVERY_LEFT,pump_opening_time);
                       break;                         
                       } 
                }
}

// ======================================== //
int reward_anticipation_period(unsigned long waitingTimeInMicroSec,int BlockType,int reading_delay,unsigned long lick_array_correct_spout[], unsigned long lick_array_incorrect_spout[], unsigned long chamber_leave_array[], int response_window){
// ======================================== //
                        if(LASER_TIME == 3 || LASER_TIME == 34) // turn on laser, if anticipation is desired stimulation period. 3 = anticipation, 34 = anticipation plus post reward
                        {
                          masking_LED_on(MASKING_LED_TRIGGER);
                            if((laser_this_block > 0) && (laser_on_bool))// only if it is a laser block
                            {                        
                               turn_laser_on();
                            }
                      }
                   int all_rec_licks = Record_lick_head_detection_during_waiting_epoch(waitingTimeInMicroSec, BlockType, reading_delay, lick_array_correct_spout, lick_array_incorrect_spout, chamber_leave_array, response_window);
                     
                  digitalWrite2f(SYNC, HIGH);
                  digitalWrite2f(LED3, HIGH);  /// Changed on 09/03/22
                  if((LASER_TIME == 3) && (laser_this_block > 0))
                        { 
                       turn_laser_off();
                        }

                        return all_rec_licks; // -1: Only incorrect licking / -2: both incorrect and correct licking / > 0 else
                  }

                  
// ======================================== //
void post_reward_period(){ //////// NEW ////////////////
// ======================================== //
   if(LASER_TIME == 4 ) // turn on laser, if post reward is desired stimulation period. 4=post reward
   {
    masking_LED_on(MASKING_LED_TRIGGER);
         if((laser_this_block > 0)&& (laser_on_bool)) // only if it is a laser block
            {
            
             turn_laser_on(); 
              }
            }
          Record_lick_head_detection_during_waiting_epoch(POST_REWARD_WAITING,licking_block_type,delay_between_licking_reading,
                                    lick_array_correct_spout_PostReward,lick_array_incorrect_spout_PostReward,chamber_leave_array_post_reward, 0);                    
          if((laser_this_block > 0)&& (laser_on_bool))
            {
            if((LASER_TIME == 4 || LASER_TIME == 34 || LASER_TIME == 234|| LASER_TIME == 1234))
              {
             turn_laser_off(); 
              }
            }
    }

// ======================================== //
void check_setup(){
// ======================================== //
unsigned long arduino_timer = micros();
// WHEN ONLY 1 SPOUT PRESENT, ONLY CHECK 1 SPOUT
if (trainingStage < 4){
    if (FIRST_BLOCK == -1){
        if((digitalRead2f(ENTER_NOSE_POKE) == LOW) && (digitalRead2f(ENTER_LICK_CHAMBER) == LOW) && (digitalRead2f(LICK_RIGHT) == HIGH)  && (arduino_timer < (10 * 60 * 1000000) ) ){
            Serial.println("COMPLETE"); 
            delay(1000);    
            }
          else
            {
            Serial.println("Nosepoke");
            Serial.println(digitalRead2f(ENTER_NOSE_POKE));
             Serial.println("should be 0");
            Serial.println("lick cham");
            Serial.println(digitalRead2f(ENTER_LICK_CHAMBER));
             Serial.println("should be 0");
            Serial.println("right lick");
            Serial.print(digitalRead2f(LICK_RIGHT));
             Serial.println("should be 1");
            Serial.println("left lick");
            Serial.print(digitalRead2f(LICK_LEFT));
             Serial.println("should be 1");
             delay(1000);
            Serial.println("ERROR");
            delay(1000);
            stop();
            }
        }
    else if (FIRST_BLOCK == 1){
         if((digitalRead2f(ENTER_NOSE_POKE) == LOW) && (digitalRead2f(ENTER_LICK_CHAMBER) == LOW) && (digitalRead2f(LICK_LEFT) == HIGH)  && (arduino_timer < (10 * 60 * 1000000) ) ){
            Serial.println("COMPLETE"); 
            delay(1000);    
            }
          else
              {
              Serial.println("Nosepoke");
              Serial.println(digitalRead2f(ENTER_NOSE_POKE));
                Serial.println("should be 0");
              Serial.println("lick cham");
              Serial.println(digitalRead2f(ENTER_LICK_CHAMBER));
               Serial.println("should be 0");
              Serial.println("right lick");
              Serial.println(digitalRead2f(LICK_RIGHT));
               Serial.println("should be 1");
              Serial.println("left lick");
              Serial.print(digitalRead2f(LICK_LEFT));
              Serial.println("should be 1");
               delay(1000);
              Serial.println("ERROR");
              delay(1000);
              stop();
              }
         }      
    }
   else{
     if((digitalRead2f(ENTER_NOSE_POKE) == LOW) && (digitalRead2f(ENTER_LICK_CHAMBER) == LOW) && (digitalRead2f(LICK_LEFT) == HIGH) && (digitalRead2f(LICK_RIGHT) == HIGH) && (arduino_timer < (10 * 60 * 1000000) ) ){
            Serial.println("COMPLETE"); 
            delay(1000);    
            }
          else
              {
              Serial.println("Nosepoke");
              Serial.println(digitalRead2f(ENTER_NOSE_POKE));
              Serial.println("should be 0");
              Serial.println("lick cham");
              Serial.println(digitalRead2f(ENTER_LICK_CHAMBER));
               Serial.println("should be 0");
              Serial.println("right lick");
              Serial.println(digitalRead2f(LICK_RIGHT));
               Serial.println("should be 1");
              Serial.println("left lick");
              Serial.print(digitalRead2f(LICK_LEFT));
              Serial.println("should be 1");
               delay(1000);
              Serial.println("ERROR");
              delay(1000);
              stop();
              }
   }
}

// ======================================== //
void stop(){
// ======================================== //
 while(1);
}

// ======================================== //
void define_python_variables(){
// ======================================== //
//Serial.println("in"); 
while(!Serial.available()) 
     {     
     //  Serial.println("in2"); 
     }      
int k = 0;
int all_data = 0;
String incoming_info;
// while loop to only receive parameters from python interface once
while(k < 1)
     {
// wait for data to arrive
     while(!Serial.available()) 
          {             
          } 
// whenever data is available, check if we have already received all parameters we want       
     while(Serial.available() && all_data <=19)
          {  
          //  Serial.println("all data less");
                  
          incoming_info = Serial.readStringUntil('\n');
          if (incoming_info.indexOf("Subject") >= 0)
             {
             incoming_info.remove(0, 7);
             Serial.println("SUB");
             Serial.println(incoming_info);
             all_data++;
             } 
          else if (incoming_info.indexOf("Train") >= 0)
            {               
            incoming_info.remove(0, 5);
            trainingStage = incoming_info.toInt();
            Serial.println("Train");
            Serial.println(trainingStage);
            all_data++;
            }
         else if (incoming_info.indexOf("Walk") >= 0)
            {               
            incoming_info.remove(0, 4);
            WALKING_WINDOWS_DURATION = incoming_info.toInt();
            Serial.println("Walk");
            Serial.println(WALKING_WINDOWS_DURATION);
            WALKING_WINDOWS_DURATION = WALKING_WINDOWS_DURATION * 1000000;
            all_data++;
            }
                
          else if (incoming_info.indexOf("Block_number") >= 0)
            {               
            incoming_info.remove(0, 12);
            BLOCK_NUMBER = incoming_info.toInt();
            Serial.println("BLOCK_NUMBER");
            Serial.println(BLOCK_NUMBER);
            all_data++;
            }
          else if (incoming_info.indexOf("Block_length") >= 0)
            { 
            incoming_info.remove(0, 12);
            BLOCK_LENGTH = incoming_info.toInt();
            Serial.println("BLOCK_LENGTH");
            Serial.println(BLOCK_LENGTH);
            all_data++;
            }
           else if (incoming_info.indexOf("First_block") >= 0)
            { 
            incoming_info.remove(0, 11);
            FIRST_BLOCK = incoming_info.toInt();
            Serial.println("FIRST_BLOCK");
            Serial.println(FIRST_BLOCK);
            all_data++;
            }
           else if (incoming_info.indexOf("ITI_length") >= 0)
            { 
            incoming_info.remove(0, 10);
            ITI_DURATION = incoming_info.toInt();
            Serial.println("ITI_LENGTH");
            Serial.println(ITI_DURATION);
            ITI_DURATION = ITI_DURATION * 1000000;
            all_data++;
            }
           else if (incoming_info.indexOf("Resp") >= 0)
            { 
            incoming_info.remove(0, 4);
            RESPONSE_WINDOWS_DURATION = incoming_info.toInt();
            Serial.println("RESPONSE");
            Serial.println(RESPONSE_WINDOWS_DURATION);
            RESPONSE_WINDOWS_DURATION = RESPONSE_WINDOWS_DURATION * 1000000;
            all_data++;
            }
            
          else if (incoming_info.indexOf("To_gate") >= 0)
            {
            incoming_info.remove(0, 7);
            TIME_NOSEPOKE_TO_OPEN_GATE = incoming_info.toInt();
            Serial.println("To_gate");
            Serial.println(TIME_NOSEPOKE_TO_OPEN_GATE);
            TIME_NOSEPOKE_TO_OPEN_GATE = TIME_NOSEPOKE_TO_OPEN_GATE * 1000;
            all_data++;
            }  
              
          else if (incoming_info.indexOf("Wait_antic") >= 0)
            { 
            incoming_info.remove(0, 10);
            WAITING_ANTICIPATION = incoming_info.toInt();
            Serial.println("WAIT_ANTIC");
            Serial.println(WAITING_ANTICIPATION);
            WAITING_ANTICIPATION = WAITING_ANTICIPATION * 1000;
            all_data++;
            }
          else if (incoming_info.indexOf("Post_rew") >= 0)
            { 
            incoming_info.remove(0, 8);
            POST_REWARD_WAITING = incoming_info.toInt();
            Serial.println("POST_REWARD");
            Serial.println(POST_REWARD_WAITING);
            POST_REWARD_WAITING = POST_REWARD_WAITING * 1000;
            all_data++;
            }
               
          else if (incoming_info.indexOf("Hit") >= 0)
            { 
            incoming_info.remove(0, 3);
            number_licks_for_hit = incoming_info.toInt();
            Serial.println("HIT");
            Serial.println(number_licks_for_hit);
            all_data++;
            }
          else if (incoming_info.indexOf("Lick") >= 0)
            { 
            incoming_info.remove(0, 4);
            delay_between_licking_reading = incoming_info.toInt();
            Serial.println("LICK_READ");
            Serial.println(delay_between_licking_reading);
            all_data++;
            }
          else if (incoming_info.indexOf("Pump") >= 0)
            { 
            incoming_info.remove(0, 4);
            pump_opening_time = incoming_info.toInt();
            Serial.println("PUMP");
            Serial.println(pump_opening_time);
            all_data++;
            }
          else if (incoming_info.indexOf("Cue") >= 0)
            { 
            incoming_info.remove(0, 3);
            RESPONSE_CUE = incoming_info.toInt();
            Serial.println("CUE");
            Serial.println(RESPONSE_CUE);
            all_data++;
            }  
          else if (incoming_info.indexOf("Las_t") >= 0)
            { 
            incoming_info.remove(0, 5);
            LASER_TIME = incoming_info.toInt();
            Serial.println("LAS_T");
            Serial.println(LASER_TIME);
            all_data++;
            } 
          else if (incoming_info.indexOf("Las_b") >= 0)
            { 
            incoming_info.remove(0, 5);
            LASER_BLOCK = incoming_info.toInt();
            Serial.println("LAS_B");
            Serial.println(LASER_BLOCK);
            all_data++;
            }   
           else if (incoming_info.indexOf("Las_p") >= 0)
            { 
            incoming_info.remove(0, 5);
            LASER_PROBABILITY = incoming_info.toInt();
            Serial.println("LAS_P");
            Serial.println(LASER_PROBABILITY);
            all_data++;
            }
          else if (incoming_info.indexOf("Wind") >= 0)
            { 
            incoming_info.remove(0, 4);
            moving_window_size = incoming_info.toInt();
            Serial.println("WIND");
            Serial.println(moving_window_size);
            all_data++;
            }  
            else if (incoming_info.indexOf("Rew_prob") >= 0)
            { 
            incoming_info.remove(0, 8);
            reward_prob = incoming_info.toInt();
            Serial.println("Rew_prob");
            Serial.println(reward_prob);
            all_data++;
            } 
          else if (incoming_info.indexOf("END") >= 0)
            {
            Serial.println("END RECEIVED");
            Serial.println(incoming_info);
            all_data++;
            }
          if (all_data > 19)
            {
// check functionality of setup
            check_setup();
            Serial.println("checked");
            k++;                           
            Serial.flush();     
            delay(1000);         
            break;  
            }
          delay(100);     
          }//end while Serial.available
    }
}

// ======================================== //
void defineTrainingParameters(int stepTraining){
// ======================================== //
switch(stepTraining) 
      { 
      case 1: //Licking training on 1 spout, flexible response window
           {
           breakLickingDetection_Hit = 1;
           breakLickingDetection_Error = 0;
           WAITING_ANTICIPATION = 0;
           trainingWithoutNosePoke = 1;
           ignoreTheIncorrectSpout = 1;
           BLOCK_NUMBER = 1; 
           gate_closes_directly_after_error = 1;
           break;
           }    
      case 2: //Integration of fixed licking response window and reward anticipation
           {
           breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 0;
           trainingWithoutNosePoke = 1;
           ignoreTheIncorrectSpout = 1;
           gate_closes_directly_after_error = 1;
           BLOCK_NUMBER = 1; 
           break;
           }    
      case 3: // Nose Poke Port
           {
            breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 0;
           trainingWithoutNosePoke = 0;
           ignoreTheIncorrectSpout = 1;
           gate_closes_directly_after_error = 1;
           BLOCK_NUMBER = 1; 
           break;
           }  
      case 4: // Spatial Discrimination, immediate error feedback
           {
          breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 1;
           trainingWithoutNosePoke = 0;
           ignoreTheIncorrectSpout = 0;
           gate_closes_directly_after_error = 1;
           BLOCK_NUMBER = 1; 
           break;
           }
      case 5: //Inter Session rev, immediate Error Feedback
           {
           breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 1;
           trainingWithoutNosePoke = 0;
           ignoreTheIncorrectSpout = 0;
           gate_closes_directly_after_error = 1;
           //BLOCK_NUMBER = 1; 
           break;
           }   
      case 6: // Inter session reversal, no immediate error feedback. Adding anticipation and postreward periods after errors and misses
           {
            breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 0;
           trainingWithoutNosePoke = 0;
           ignoreTheIncorrectSpout = 0;
           gate_closes_directly_after_error = 0;
           BLOCK_NUMBER = 1; 
           break;
           }  
      case 7: // Intra Session Reversal
           {
           breakLickingDetection_Hit = 0;
           breakLickingDetection_Error = 0;
           trainingWithoutNosePoke = 0;
           ignoreTheIncorrectSpout = 0;
           gate_closes_directly_after_error = 0;
           break;
           }        
       
      }
}                                   
// 1st training Step: (breakLickingDetection_Hit = 1) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 0 sec) / (trainingWithoutNosePoke = 1) / (ignoreTheIncorrectSpout = 1) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 2nd training Step: (breakLickingDetection_Hit = 0) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 1) / (ignoreTheIncorrectSpout = 1) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 3rd training Step: (breakLickingDetection_Hit = 0) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 0) / (ignoreTheIncorrectSpout = 1) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 4th training Step: (breakLickingDetection_Hit = 0) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 0) / (ignoreTheIncorrectSpout = 0) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 5th training Step: (breakLickingDetection_Hit = 0) / ( breakLickingDetection_Error = 1) /(WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 0) / (ignoreTheIncorrectSpout = 0) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 6th training Step: (breakLickingDetection_Hit = 0) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 0) / (ignoreTheIncorrectSpout = 0) / BLOCK_NUMBER = 1 / FIRST_BLOCK 0=Right or 1= LEFT 
// 7th training Step: (breakLickingDetection_Hit = 0) /( breakLickingDetection_Error = 0) / (WAITING_ANTICIPATION = 1 sec) / (trainingWithoutNosePoke = 0) / (ignoreTheIncorrectSpout = 0) / BLOCK_NUMBER = 2 or 3 / FIRST_BLOCK 0=Right or 1= LEFT

// ======================================== //
void data_transfer(){
// ======================================== //
int first_transfer = 1;
int message_received = 0;
String incoming_info;
//send data to python, wait for confirmation
while(message_received < 1)
     { 
     //on first data transfer iteration, just send everything. afterwards, first check for "received" signal          
     if(first_transfer == 1)
       {
         send_all_variables_to_python();
         first_transfer = 0;
         Serial.flush();   
       }
     //after first data transfer attempt, always check for "received" signal from python first
     else
       {
        if (Serial.available()>0)
          {        
            // incoming_info = Serial.readStringUntil('\n'); // this will be stuck for 1 seocond if nothing is incoming   
            incoming_info = Serial.readString();      
             if(incoming_info.indexOf("rec") >= 0)    
               {          
               message_received = 1;
               Serial.flush();
               break;
               }
          }
        // data transfer; repeated until confirmation signal has been sent by interface
       else 
         {   
         send_all_variables_to_python();         
         Serial.flush();
         delay(500);
          }
         
       }
     }
}

// ======================================== //
void send_all_variables_to_python(){
// ======================================== //
delay(100);
Serial.print("blo");
Serial.println(licking_block_type);
Serial.print("lio");
Serial.println(licking_result_w_lick_number);
Serial.print("light");
Serial.println(light_on_time);
Serial.print("enp");
Serial.println(enter_nose_poke_port_time);
Serial.print("lnp");
Serial.println(leave_nose_poke_port_time);
Serial.print("elc");
Serial.println(enter_lick_chamber_time);
Serial.print("om");
Serial.println(omission_time);
Serial.print("cue");
Serial.println(auditory_cue_time);  
Serial.print("err");
Serial.println(error_time);
Serial.print("mi");
Serial.println(miss_time);
Serial.print("hit");
Serial.println(hit_time);
Serial.print("rew");
Serial.println(reward_delivery_time);
Serial.print("tel");
Serial.println(trial_end);
Serial.print("pts");
Serial.println(python_transfer_start_time);   

//laser
Serial.print("lon");
Serial.println(laser_on_time);
Serial.print("loff");
Serial.println(laser_off_time);  
// print arrays
Serial.println();
Serial.print("lal"); 
print_array(lick_array, lick_array_length);  
Serial.println();  
Serial.print("lar");
 print_array(lick_array_Error, lick_array_length);    
Serial.println();
Serial.print("cs");
print_array(lick_array_correct_spout_Anticipation, lick_array_length);
Serial.println();
Serial.print("ua");
print_array(lick_array_incorrect_spout_Anticipation, lick_array_length);
Serial.println();
Serial.print("clp"); 
print_array(lick_array_correct_spout_PostReward, lick_array_length);
Serial.println();
Serial.print("up");
print_array(lick_array_incorrect_spout_PostReward, lick_array_length);
Serial.println();
Serial.print("crw");
print_array(chamber_leave_array_response_window,lick_array_length);
Serial.println();
Serial.print("ca");
print_array(chamber_leave_array_anticipation, lick_array_length);
Serial.println();
Serial.print("cpr");
print_array(chamber_leave_array_post_reward, lick_array_length);
Serial.println();
python_transfer_end_time = micros() - session_start_time;
Serial.print("pte");
Serial.println(python_transfer_end_time);    
}

// ======================================== //
void  end_session(){
// ======================================== //
pulses_signal(SYNC,9, 1);      
while(1){
digitalWrite2f(NOSE_POKE_PORT_LIGHT, LOW);
digitalWrite2f(LICK_CHAMBER_LIGHT, LOW);
session_end_time = micros() - session_start_time;

Serial.print("done"); 
Serial.println(session_end_time);
delay(100);

}
}

// ======================================== //
void  manual_end_session(){
// ======================================== //
finished_blocks=BLOCK_NUMBER;
}

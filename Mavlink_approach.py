from dronekit import connect
from pymavlink import mavutil
import pandas as pd
import time

# Read df
df = pd.read_excel('dataset/dummy.xlsx')

# Connect to the drone
connection_string = '/dev/ttyACM0'

vehicle = connect(connection_string, wait_ready = True)

try:
    # Check param
    for i in range(6):
        servo_parm = 'SERVO%s_FUNCTION'% (i+1)
        if int(vehicle.parameters[servo_parm])!=1:
            vehicle.parameters[servo_parm]=1
            while int(vehicle.parameters[servo_parm])!=1:
                time.sleep(1)
            print(servo_parm+' is set to 1 already.')
        else:
            print(servo_parm+' is set to 1 already.')
                    
    time.sleep(2)

    channel = ['1','2','3','4','5','6']
    # Pre_arm
    for chan in channel:
        vehicle.channels.overrides[chan] = 1200

    msg = vehicle.message_factory.command_long_encode(
        0,0,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        9,
        1900,
        0,0,0,0,0
        )

    vehicle.send_mavlink(msg)
        
    time.sleep(5)
        
    # vehicle.channels.overrides['8'] = 1900

    # set RC
    for i in range (len(df)):
        pwm_lst = df.iloc[i,1:7].tolist()
        final_lst = list(map(int, pwm_lst))
        channel_dict = {}
        count = 0
        for j in final_lst:
            count +=1
            channel_dict[str(count)]=j
        vehicle.channels.overrides = channel_dict
        print(" Channel overrides: %s" % vehicle.channels.overrides)
        print(" Ch1: %s" % vehicle.channels['1'])
        print(" Ch2: %s" % vehicle.channels['2'])
        print(" Ch3: %s" % vehicle.channels['3'])
        print(" Ch4: %s" % vehicle.channels['4'])
        print(" Ch5: %s" % vehicle.channels['5'])
        print(" Ch6: %s" % vehicle.channels['6'])
        time.sleep(0.09)
        
    print("Clear all overrides")
    vehicle.channels.overrides = {}

    # Reset param
    for i in range(6):
        servo_parm = 'SERVO%s_FUNCTION'% (i+1)
        vehicle.parameters[servo_parm]=33+i
        
    #vehicle.parameters['SERVO8_FUNTION']=56
    msg = vehicle.message_factory.command_long_encode(
        0,0,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        9,
        1100,
        0,0,0,0,0
        )

    vehicle.send_mavlink(msg)

except KeyboardInterrupt:
    print("STOP!")
    print("Clear all overrides")
    vehicle.channels.overrides = {}

    # Reset param
    for i in range(6):
        servo_parm = 'SERVO%s_FUNCTION'% (i+1)
        vehicle.parameters[servo_parm]=33+i
        
    #vehicle.parameters['SERVO8_FUNTION']=56
    msg = vehicle.message_factory.command_long_encode(
        0,0,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0,
        9,
        1100,
        0,0,0,0,0
        )

    vehicle.send_mavlink(msg)

#Close connection
vehicle.close()
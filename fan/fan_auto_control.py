from common_config import create_client
import time



class FanAutoControl:
    def __init__(self, sp_flowrate = 200, client = None):
        if client is None:
            self.client = create_client()
        else:
            self.client = client
        self.sp_flowrate = sp_flowrate

        self.sp_flrt_topic = "master/outlet/sp_flowrate"
        self.client.message_callback_add(self.sp_flrt_topic, self.on_sp_flrt_message)
        self.client.subscribe(self.sp_flrt_topic)
        
        # PID parameters
        self.K_p = 0.3
        self.K_i = 0.01
        # self.K_d = 0.05

        self.integral = 0
        self.previous_error = 0
        self.last_time = time.time()

        self.output_topic_in = "master/inlet/fan_in_auto"
        self.output_topic_out = "master/outlet/fan_out_auto"

        self.client.message_callback_add("slave/outlet/flowrate", self.on_flowrate_message)
        self.client.subscribe("slave/outlet/flowrate")


    def on_sp_flrt_message(self, client, userdata, msg):
        try:
            new_sp_flowrate = int(msg.payload.decode())
            self.sp_flowrate = new_sp_flowrate
            self.integral = 0
            print(f"[Fan Control] Auto-control: New flowrate setpoint received: {self.sp_flowrate} m3/h")
        except Exception as e:
            print(f"[Fan Control] Auto-control error: {e}")


    def on_flowrate_message(self, client, userdata, msg):
        try:
            current_flowrate = float(msg.payload.decode())
            print(f"Received flowrate data from flowmeter: {current_flowrate}")
            now = time.time()
            dt = now - self.last_time
            
            # calculating PID output
            error = self.sp_flowrate - current_flowrate
            new_integral = self.integral + error*dt
            potential_output = self.K_p*error + self.K_i*(self.integral + error*dt)
            if 0<=potential_output<=100:
                self.integral = new_integral
            output = self.K_p*error + self.K_i*self.integral

            if output<15:
                fan_output = 0
            elif output<=30:
                fan_output = 30
            else:
                fan_output = int(max(min(output, 100),30))

            self.client.publish(self.output_topic_in, str(fan_output))
            self.client.publish(self.output_topic_out, str(fan_output))
            print(f"Errpr: {error}, Output: {output}%")

            self.previous_error = error
            self.last_time = now
        except Exception as e:
            print(f"[Fan Control] Auto-control error: {e}")
    

    def set_target(self, new_sp):
        self.sp_flowrate = new_sp
        self.integral = 0

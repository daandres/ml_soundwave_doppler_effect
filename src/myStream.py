from pyaudio import Stream 

class MyStream(Stream):
    
    def __init__(self, stream):
        Stream.__init__(self,
                 stream._parent,
                 stream._rate,
                 stream._channels,
                 stream._format,
                 input=stream._is_input,
                 output=stream._is_output,
                 input_device_index=None,
                 output_device_index=None,
                 frames_per_buffer=1024,
                 start=stream._is_running,
                 input_host_api_specific_stream_info=None,
                 output_host_api_specific_stream_info=None,
                 stream_callback=None)
        stream.close()
        
    def tell(self):
        return 1   
    
    def seek(self, offset, whence):
        return 0 
    
    def flush(self):
        return 0
    
    def stopIt(self):
        self.stop_stream()
        self.close()
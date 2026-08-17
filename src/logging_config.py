import json,logging
class JsonFormatter(logging.Formatter):
 def format(self,record):return json.dumps({"timestamp":self.formatTime(record),"severity":record.levelname,"message":record.getMessage(),"job_id":getattr(record,"job_id",None),"stage":getattr(record,"stage",None),"exception_type":record.exc_info[0].__name__ if record.exc_info else None})
def configure_logging(level:int=logging.INFO):
 handler=logging.StreamHandler();handler.setFormatter(JsonFormatter());root=logging.getLogger();root.handlers=[handler];root.setLevel(level)


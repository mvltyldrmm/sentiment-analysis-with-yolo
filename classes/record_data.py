import uuid
class records_data:                         
   def __init__(self, name, description, total_time, emotion_analytics): 
     self.uuid = uuid.uuid4()                           
     self.name = name
     self.description = description
     self.total_time = total_time
     self.emotion_analytics = emotion_analytics


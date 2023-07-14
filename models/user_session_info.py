import threading

class UserSessionInfo:
    _instances = threading.local()

    def __init__(self):
        self.accountID = None
        self.firstName = None
        self.lastName = None
        self.linkedinProfile = None
        self.sessionID = None
        self.email = None
        self.whisper = None
        self.turn = 0
        self.generated_text = None
        self.transcribed_text = None

    @classmethod
    def get_instance(cls):
        if not hasattr(cls._instances, "instance"):
            cls._instances.instance = UserSessionInfo()
        return cls._instances.instance

    def update_info(self, accountID, firstName,lastName,sessionID,linkedinProfile,whisper,email,turn,transcribed_text,generated_text):
        self.accountID = accountID
        self.sessionID = sessionID
        self.whisper = whisper
        self.firstName = firstName
        self.lastName = lastName
        self.linkedinProfile = linkedinProfile
        self.email = email
        self.turn = turn
        self.transcribed_text = transcribed_text
        self.generated_text = generated_text
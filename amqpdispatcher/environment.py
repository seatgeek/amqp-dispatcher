import os


class Environment(object):
    app_name: str

    def __init__(self):
        self.app_name = os.getenv("APP", "")
        self.nomad_alloc_id = os.getenv("NOMAD_ALLOC_ID", "")
        self.nomad_job_name = os.getenv("NOMAD_JOB_NAME", "")

    @classmethod
    def create(cls):
        return Environment()
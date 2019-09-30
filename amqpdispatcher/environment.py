import os


class Environment(object):
    app_name: str

    def __init__(self) -> None:
        self.app_name = os.getenv("APP", "")
        self.nomad_alloc_id = os.getenv("NOMAD_ALLOC_ID", "")
        self.nomad_job_name = os.getenv("NOMAD_JOB_NAME", "")
        self.rabbit_url = os.getenv(
            "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"
        )

    @classmethod
    def create(cls) -> 'Environment':
        return Environment()

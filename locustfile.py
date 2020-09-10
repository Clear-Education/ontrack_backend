from locust import HttpUser, TaskSet, task


class WebsiteActions(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        # login to the application
        response = self.client.post(
            "api/users/login/",
            {"username": "locust@locust.com", "password": "locust1234321"},
        )
        self.token = response.json()["token"]
        # self.token = response.data['token']

    @task(2)
    def list_users(self):
        self.client.get(
            "api/users/list/",
            headers={"authorization": "Token " + self.token},
        )

    @task(3)
    def list_seguimientos(self):
        self.client.get(
            "api/seguimientos/list/",
            headers={"authorization": "Token " + self.token},
        )

    @task(1)
    def admin(self):
        self.client.get("admin/")


class ApplicationUser(HttpUser):
    tasks = [WebsiteActions]
    min_wait = 5000
    max_wait = 15000

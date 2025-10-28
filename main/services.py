from .repositories import MainRepository


class MainService:
    def __init__(self):
        self.repo = MainRepository()

    def get_main_data(self):
        context = {
            'total_campaigns': self.repo.get_total_campaing,
            'total_influencers': self.repo.get_total_influencers,
            'total_users': self.repo.get_total_users,
        }
        return context

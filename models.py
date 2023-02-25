class User:
    def __init__(self, id, first_name = None, second_name = None, age = None, sex = None, city = None, region = None, interests = None) -> None:
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.age = age
        self.sex = sex
        self.city = city
        self.region = region
        self.interests = interests
    
    def get_data(self):
        return self.id, self.first_name, self.second_name, self.age, self.sex, self.city, self.region, self.interests
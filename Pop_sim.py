import numpy as np
from faker import Faker
import random
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter

fake = Faker()

debug = False

"""

Implement genetics system: 
    inherit good or bad traits
    eugenics pushes for good traits
    but small gene pool makes emergence of bad traits more likely

"""

class Person:
    ID = 0

    def __init__(self, age):
        Person.ID += 1
        self.ID = Person.ID
        self.age = age
        self._surname = None
        # Define is_child based on age
        self.is_child = True if self.age < 18 else False
        # 50/50 gender probability
        self.gender = random.choice(["male", "female"])
        if self.gender == "male":
            self.first_name = fake.first_name_male()
        elif self.gender == "female":
            self.first_name = fake.first_name_female()
        self.name = self.first_name

    @property
    def surname(self):
        return self._surname

    @surname.setter
    def surname(self, value):
        self._surname = value
        if self._surname is not None:
            self.name = self.first_name + " " + self._surname

        # Recent stats: 3% of population is homosexual and 4% is bisexual
        orientation_prob = random.random()
        if orientation_prob < 0.03:
            orientation = "homosexual"
        elif orientation_prob < 0.07:
            orientation = "bisexual"
        else:
            orientation = "heterosexual"
        self.orientation = orientation

        if self.orientation == "heterosexual":
            if self.gender == "male":
                self.spouse_gender = "female"
            else:
                self.spouse_gender = "male"
        elif self.orientation == "homosexual":
            if self.gender == "male":
                self.spouse_gender = "male"
            else:
                self.spouse_gender = "female"
        else:
            self.spouse_gender = ["male", "female"]

        if self.age < 18:
            self.is_child = True
        else:
            self.is_child = False

        self.spouse = None
        self.parents = []
        self.children = []


class Family:
    def __init__(self, parents, surname):
        self.parents = parents
        self.surname = surname
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        for parent in self.parents:
            parent.children.append(child)


def simulate_population(population_size, initial_family_count, debug, time_steps):
    fake = Faker()
    Faker.seed(0)  # Set seed for consistent data generation

    population = []
    families = []
    step = 0
    AVG_LIFESPAN = 80 + (step // 10)




    # Initialize the population
    print("Initializing the population...")
    print("Initializing age distribution...")
    age_distribution = [random.randint(0, 15) for _ in range(int(population_size * 0.55))] + [random.randint(35, 60) for
                        _ in range(int(population_size * 0.45))]

    surnames = set()
    # Populate array of unique surnames
    while len(surnames) < population_size / 2:
        surname = fake.last_name()
        if surname not in surnames:
            surnames.add(surname)

    if debug:
        print(f"{len(surnames)} total surnames generated. ")
        for surname in surnames:
            print(surname)

    print("Initializing raw population...")
    debug_counter = 0
    for i in range(population_size):
        # Initialize the population with age according to the age distribution
        age = age_distribution[i]
        # Initialize person
        person = Person(age)
        # Add person to population
        population.append(person)

        # Give adults a surname
        if person.is_child is False:
            try:
                print(list(surnames))
                person.surname = random.choice(list(surnames))
                # Remove surname from pool once assigned to assure uniqueness
                surnames.remove(person.surname)
            except:
                print("Error: Not enough surnames to assign to population. Len: " + str(len(surnames)))
                exit(1)
        else:
            person.surname = None

        if debug:
            debug_counter+=1
            print(f"{debug_counter} Surname assigned: " + person.name)



    counter = Counter(person.surname for person in population)
    duplicates = [item for item, count in counter.items() if count > 1 and item is not None and item is not True]
    if debug:
        print("duplicates = " + str(duplicates))
    if len(duplicates) > 0:
        print("Error: Duplicate surnames detected: " + str(len(duplicates)) + ' ' + str(duplicates))
        exit(1)

    for person in population:
        if person.is_child is False:
            print(person.name)

    # DEBUG: Print population statistics


    # if debug is True:
    #     # for person in population:
    #     #    print(person.name + ' ' + str(person.age))
    #     max_age = max(person.age for person in population)
    #     print(f"Minimum age: {min(person.age for person in population)}")
    #     print(f"Maximum age: {max_age}")
    #     age_histogram = [0] * (max_age + 1)
    #     orientation_histogram = [0] * 3
    #
    #     for person in population:
    #         if person.age <= max_age:
    #             age_histogram[person.age] += 1
    #         else:
    #             age_histogram.append(1)
    #             max_age += 1
    #
    #     plt.bar(range(len(age_histogram)), age_histogram)
    #     plt.xlabel('Age')
    #     plt.ylabel('Population Count')
    #     plt.title('Population Demographics by Age, Initial Population')
    #     plt.show()
    #
    #     total_males = 0
    #     for person in population:
    #         if person.gender == "male":
    #             total_males += 1
    #     print(f"Total males: {total_males}\nTotal females: {500 - total_males}\nGender ratio: {total_males / 500}")
    #
    #     for person in population:
    #         if person.orientation == "heterosexual":
    #             orientation_histogram[0] += 1
    #         elif person.orientation == "homosexual":
    #             orientation_histogram[1] += 1
    #         else:
    #             orientation_histogram[2] += 1
    #
    #     labels = ["heterosexual", "homosexual", "bisexual"]
    #     x = range(len(orientation_histogram))
    #     plt.bar(x, orientation_histogram, tick_label=labels)
    #     plt.show()

    # Simulate population dynamics for the given number of time steps (years)
    print("Simulating population dynamics...")
    max_age = max(person.age for person in population)
    age_histogram = [0] * (max_age + 1)
    for step in range(time_steps):
        print(f"Simulating year {step}...")
        # Update ages and track demographics
        print("Aging population...")
        for person in population:
            person.age += 1
            if person.age <= max_age:
                age_histogram[person.age] += 1
            else:
                age_histogram.append(1)
                max_age += 1

        # Determine who dies (based on age and life expectancy)
        # Define Gompertz-Makeham parameters
        alpha = 0.05  # Baseline mortality rate
        beta = 0.001  # Rate of age-related increase in mortality

        print("Determining mortality due to old age...")
        # Determine who dies based on age and Gompertz-Makeham distribution
        for family in families:
            for parent in family.parents:
                age_difference = parent.age - AVG_LIFESPAN
                if age_difference >= 0:
                    survival_probability = np.exp(alpha + beta * age_difference)
                    if random.random() > survival_probability:
                        family.parents.remove(parent)
                        population.remove(parent)
                        print(f"{parent.first_name} {parent.surname} died at age {parent.age}")


        print("Generating families...")
        # Allow couples to form families and have children
        eligible_parents = [person for person in population if 20 <= person.age <= 50]
        print("Generating parenting couples...")
        parents = []
        print(", " .join(person.name for person in eligible_parents))
        while len(eligible_parents) >= 2:

            while True:
                print("Choosing first parent...")
                parents.append(random.choice(eligible_parents))
                print(f"Parent: {parents[0].name}, {parents[0].age}, {parents[0].orientation}\n\n")
                print("Eligible parents: " + str(len(eligible_parents)))
                while True:
                    parents.append(random.choice(eligible_parents))
                    for person in parents:
                        print(f"Person: {person.name}, {person.age}, {person.orientation}, {person.spouse_gender}")

                    if debug is True:
                        if len(parents) == 2:
                            print("First parent gender:", parents[0].gender)
                            print("First parent spouse gender:", parents[0].spouse_gender)
                            print("Second parent gender:", parents[1].gender)
                            print("Second parent spouse gender:", parents[1].spouse_gender)


                    if parents[1].gender in parents[0].spouse_gender and parents[0].gender in parents[1].spouse_gender:
                        print("Eligible\n")

                        eligible_parents.remove(parents[0])
                        eligible_parents.remove(parents[1])
                        break
                    else:
                        print("Not eligible\n")
                        parents.remove(parents[1])

                if parents[0].gender in parents[1].spouse_gender and parents[1].gender in parents[0].spouse_gender:
                    print("Couple formed!")
                    # If hetero, assign male surname, otherwise doesn't matter
                    if parents[0].gender == "male":
                        parents[1].surname = parents[0].surname
                    else:
                        parents[0].surname = parents[1].surname
                    for parent in parents:
                        print(f"{parent.name}, {parent.age}, {parent.orientation}")
                    family_surname = parents[0].surname

                print("Remaining eligible parents: " + str(len(eligible_parents)))
                if len(parents) != 2:
                    print("Parents need to be two. Resetting...")
                    parents = []
                    continue
                break


            # Assign spouses
            if len(parents) != 2:
                exit(1)
            parents[0].spouse = parents[1]
            parents[1].spouse = parents[0]

            family = Family(parents, family_surname)
            families.append(family)

            # Assigned any children without parents to this family, up to 3
            print("Assigning children to family...")
            for person in population:
                # If child without parents, assign to family
                if person.is_child is True and person.parents == []:
                    person.parents = parents
                    # Patriarchal surname assignment
                    if parents[0].gender == "male":
                        person.surname = parents[0].surname
                    else:
                        person.surname = parents[1].surname
                    # Add child to family
                    family.add_child(person)
                    print(f"Assigned {person.name} to family {family_surname}")
                    # If family has 3 children, stop assigning children to this family
                    if len(family.children) >= 3:
                        break


            # if population capacity not yet reached, have children
            if len(population) < population_size:
                print("Adding children to the population...")
                child_surname = family_surname
                child = Person(0, child_surname)
                family.add_child(child)
                population.append(child)
                eligible_parents.append(child)
                print(f"{parents[0].name} and {parents[1].name} had a baby named {child.first_name}!")

        # Print family lineages
        if step % 10 == 0:
            print(f"Family Lineages at Year {step}:")
            for i, family in enumerate(families):
                if i >= 10:
                    break
                print(f"Couples: {', '.join([parent.name for parent in family.parents])}")
                for child in family.children:
                    print(f"   Child: {child.name} ({child.gender})")

    # Plot age histogram
    plt.bar(range(len(age_histogram)), age_histogram)
    plt.xlabel('Age')
    plt.ylabel('Population Count')
    plt.title('Population Demographics by Age')
    plt.show()

    # View lineage of a person
    def view_lineage(person):
        G = nx.DiGraph()

        # Create nodes for each person
        for p in population:
            G.add_node(p.name)

        # Create edges for family relationships
        for family in families:
            for child in family.children:
                parent1_name = family.parents[0].name
                parent2_name = family.parents[1].name
                child_name = child.name
                G.add_edge(parent1_name, child_name)
                G.add_edge(parent2_name, child_name)

        # Draw family tree
        pos = nx.spring_layout(G)
        nx.draw_networkx(G, pos=pos, with_labels=True)
        plt.axis('off')
        plt.show()

    # Select a person and view their lineage
    if len(population) > 0:
        selected_person = random.choice(population)
        view_lineage(selected_person)


# Run the simulation
population_size = 500
initial_family_count = 112
family_size = 4.5
time_steps = 100

simulate_population(population_size, initial_family_count, family_size, time_steps)

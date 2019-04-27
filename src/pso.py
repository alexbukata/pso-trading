import random


def optimize(params, fitness, n_particles=5):
    swarm = _initialize(params, fitness, n_particles)
    global_min_fitness = swarm.min_particle.fitness
    global_min_fitness_early_stopping_rounds = 20
    k = 0
    while True:
        k += 1
        if k % 10 == 0:
            print(k)
        for particle in swarm.particles:
            velocity = {}
            for name, value in particle.values.items():
                dim_velocity = swarm.inertia * particle.velocity[name] \
                               + swarm.local_extremum_weight * random.uniform(0, 1) * (particle.local_min_state[name] - value) \
                               + swarm.global_extremum_weight * random.uniform(0, 1) * (swarm.min_particle.value(name) - value)
                velocity[name] = dim_velocity
                if (particle._id == 1):
                    print(dim_velocity)
            particle.move(velocity)
        swarm.fitness()
        if swarm.min_particle.fitness < global_min_fitness:
            global_min_fitness = swarm.min_particle.fitness
            global_min_fitness_early_stopping_rounds = 20
        elif global_min_fitness_early_stopping_rounds == 0:
            break
        else:
            global_min_fitness_early_stopping_rounds -= 1
    return swarm


def _initialize(params, fitness, n_particles):
    swarm = Swarm()
    for n in range(n_particles):
        particle = Particle(n, fitness)
        for name, type, min, max in params:
            if type is int:
                particle.create(name, random.randint(min, max), (type, min, max))
            elif type is float:
                particle.create(name, random.uniform(min, max), (type, min, max))
        swarm.add_particle(particle)
    return swarm


class Swarm:
    def __init__(self):
        self._particles = []
        self._global_min_fitness = 2 ** 32
        self._inertia = 0.3
        self._local_extremum_weight = 1
        self._global_extremum_weight = 3
        self._global_min_particle = None

    def add_particle(self, particle):
        self._particles.append(particle)
        if particle.fitness < self._global_min_fitness:
            self._global_min_fitness = particle.fitness
            self._global_min_particle = particle

    def fitness(self):
        self._global_min_fitness = self._particles[0].fitness
        self._global_min_particle = self._particles[0]
        for particle in self._particles:
            if particle.fitness < self._global_min_fitness:
                self._global_min_fitness = particle.fitness
                self._global_min_particle = particle

    @property
    def min_particle(self):
        self.fitness()
        return self._global_min_particle

    @property
    def inertia(self):
        return self._inertia

    @property
    def local_extremum_weight(self):
        return self._local_extremum_weight

    @property
    def global_extremum_weight(self):
        return self._global_extremum_weight

    @property
    def particles(self):
        return self._particles

    def __str__(self):
        particles = "\n\t".join((str(x) for x in self._particles))
        return f"Swarm=(\n\t{particles}, \n\tglobal_min={self._global_min_particle})"


class Particle:
    def __init__(self, id, fitness):
        self._id = id
        self._values = {}
        self._sources = {}
        self._fitness = fitness
        self._fitness_value = 0
        self._local_min_fitness = 0
        self._local_min_state = None
        self._last_velocity = {}
        self._changed = False

    def create(self, name, value, source):
        self._values[name] = value
        self._sources[name] = source
        self.velocity[name] = 0
        self._changed = True

    def move(self, velocity):
        for name, dim_velocity in velocity.items():
            self.values[name] = self.values[name] + dim_velocity
        self._last_velocity = velocity
        self._changed = True

    @property
    def fitness(self):
        if self._changed:
            self._fitness_value = self._fitness(self._values)
            self._changed = False
        if self._fitness_value < self._local_min_fitness:
            self._local_min_fitness = self._fitness_value
            self._local_min_state = dict(self._values)
        return self._fitness_value

    @property
    def velocity(self):
        return self._last_velocity

    @velocity.setter
    def velocity(self, velocity):
        self._last_velocity = velocity

    @property
    def values(self):
        return self._values

    def value(self, name):
        return self._values[name]

    @property
    def local_min_state(self):
        return self._local_min_state if self._local_min_state is not None else self._values

    def __str__(self):
        return f"Particle=(id={self._id}, values={self._values}, fitness={self._fitness_value})"

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    random.seed(42)
    print(optimize([("a", int, 10, 20)], lambda x: x['a'] ** 2))

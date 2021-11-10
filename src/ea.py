from src.gan import get_model
from src.gui import GUI, PLT_GUI
from src.utils import set_seed, torch_to_pil, torch_to_np
import torch
import tqdm


class Evolutionary_algorithm(object):

    def __init__(self, gan_args={}, gui_args={}, n_population=20, n_new=2,
                 p_mutation=0.5, batch_size=4, use_gui=True, seed=None):

        self.model = get_model(**gan_args)
        self.device = self.model.device
        self.use_gui = use_gui
        self.gui = GUI(**gui_args) if use_gui else PLT_GUI(**gui_args)
        self.n_population = n_population
        self.d_population = self.model.config.latentVectorDim
        self.n_new = n_new
        self.p_mutation = p_mutation
        self.batch_size = batch_size

        if seed:
            set_seed(seed)

    def init_population(self, size):
        return torch.randn(size, self.d_population).to(self.device)

    def crossover(self, population, n_children):
        if n_children == 0:
            return torch.empty([0, self.d_population], dtype=population.dtype).to(self.device)

        children = []
        n_parents = population.shape[0]

        for _ in range(n_children):
            parent_idxs = torch.multinomial(
                torch.ones(n_parents), 2, replacement=False)
            parent_a, parent_b = torch.unbind(population[parent_idxs], 0)
            mask = torch.rand(self.d_population, ).to(self.device) > 0.5
            child = torch.where(mask, parent_a, parent_b)
            children.append(child)

        children = torch.stack(children, dim=0)

        return children

    def fitness_function(self, population):
        images_tr = []
        wraper = (lambda x: x) if population.is_cuda else tqdm.tqdm
        for step in wraper(range(0, population.shape[0], self.batch_size)):
            with torch.no_grad():
                images_batch = self.model.test(
                    population[step: step + self.batch_size])
            images_tr.append(images_batch)

        images_tr = torch.cat(images_tr).to(self.device)
        if self.use_gui:
            images = torch_to_pil(images_tr)
        else:
            images = torch_to_np(images_tr)
        reset_flag, exit_flag, mask = self.gui.render(images)

        return reset_flag, exit_flag, mask

    def mutation(self, population):
        mask1 = torch.rand(population.shape[0]).to(
            self.device)[:, None] < self.p_mutation

        mask2 = torch.rand(population.shape).to(
            self.device) < self.p_mutation

        mask = mask1 & mask2

        noise = self.init_population(population.shape[0])
        mutated_population = torch.where(mask, noise, population)

        return mutated_population

    def run(self):
        population = self.init_population(self.n_population)

        while True:
            reset_flag, exit_flag, mask = self.fitness_function(population)
            n_selected = sum(mask)

            if exit_flag:
                break
            if reset_flag or n_selected == 0:
                population = self.init_population(self.n_population)
                continue

            old_members = population[mask]

            n_crossover = max(0, self.n_population - n_selected - self.n_new)
            if n_selected == 1:
                n_crossover = 0

            crossocver_members = self.crossover(old_members, n_crossover)

            mutated_members = self.mutation(old_members)

            n_new = self.n_population - n_selected - n_crossover
            new_members = self.init_population(n_new)
            population = torch.cat(
                (mutated_members, crossocver_members, new_members), dim=0)

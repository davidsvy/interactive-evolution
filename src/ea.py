from src.gan import get_model
from src.gui import GUI, PLT_GUI
from src.utils import set_seed, torch_to_pil, torch_to_np
import torch
import tqdm


class Evolutionary_algorithm(object):
    """Simple Interactive Evolutionary Algorithm.

    The new generation is created with the following steps:
    selected_members <- gui_selection(population)
    crossover_members <- crossover(selected_members)
    mutated_members <- mutation(selected_members)
    new_members <- random_noise()
    new_population <- concat(crossover_members, mutated_members, new_members)

    Attributes:
        model: pretrained gan from src/gan.py.
        device (torch.device): Device for pytorch.
        use_gui (bool): Whether to use tkinter GUI.
        gui: GUI used for image selection.
        n_population (int): Population size. Kept stable during all generations.
        d_population (int): Vector dimension of each member of the population.
        n_new (int): Number of new members added to the population at each turn.
        p_mutation (float): Probability of mutation
        batch_size (int): Batch size for gan inference.
    """

    def __init__(self, gan_args={}, gui_args={}, n_population=20, n_new=2,
                 p_mutation=0.5, batch_size=4, use_gui=True, seed=None):
        """Initializes the module.

        Args:
            gan_args (dict): Args for the pretrained gan. See src/gan.py.
            gui_args (dict): Args for the gui. See src/gui.py.
            n_population (int): Population size. Kept stable during all generations.
            n_new (int): Number of new members added to the population at each turn.
            p_mutation (float): Probability of mutation
            batch_size (int): Batch size for gan inference.
            use_gui (bool): Whether to use tkinter GUI.
            seed (int or None): If None, no seeds will be set.
        """
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
        """Returns a random population"""
        return torch.randn(size, self.d_population).to(self.device)

    def crossover(self, population, n_children):
        """Performs crossover.

        The result of the crossover between 2 vectors is a new vector where
        each eleement has a 50% probability of being from the first vector 
        and 50% from the second. The 2 parents are randomly sampled from 
        the population. This process is repeated n_children times.

        Args:
            population (torch.tensor)[x, d_population]:
            n_children (int): Number of children that must be created with
                crossover.

        Returns:
            (torch.tensor)[n_children, d_population]: 
        """
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
        """Obtains selection fitness from the gui.

        Args:
            population (torch.tensor)[n_population, d_population]:

        Returns:
            reset_flag (bool): True if the Reset button was pressed.
            exit_flag (bool): True if the Exit button was pressed.
            img_status (list(bool)): i-th element is True if the i-th image was selected.
        """
        images_tr = []
        wraper = (lambda x: x) if population.is_cuda else tqdm.tqdm
        # Feed the latents into the gan to obtain images
        for step in wraper(range(0, population.shape[0], self.batch_size)):
            with torch.no_grad():
                images_batch = self.model.test(
                    population[step: step + self.batch_size])
            images_tr.append(images_batch)

        images_tr = torch.cat(images_tr).to(self.device)
        # Transform torch.tensor into PIL or numpy
        if self.use_gui:
            images = torch_to_pil(images_tr)
        else:
            images = torch_to_np(images_tr)
        # Receive mask and flags from gui
        reset_flag, exit_flag, mask = self.gui.render(images)

        return reset_flag, exit_flag, mask

    def mutation(self, population):
        """Applies crossover.

        Each member has a p_mutation probability of being mutated, 
        in which case each of its vector elements has a p_mutation
        probability of being replaced with random uniform noise.

        Args:
            population (torch.tensor)[x, d_population]:

        Returns:
            torch.tensor)[x, d_population]: Mutated population
        """
        mask1 = torch.rand(population.shape[0]).to(
            self.device)[:, None] < self.p_mutation

        mask2 = torch.rand(population.shape).to(
            self.device) < self.p_mutation

        mask = mask1 & mask2

        noise = self.init_population(population.shape[0])
        mutated_population = torch.where(mask, noise, population)

        return mutated_population

    def run(self):
        """Runs the interactive evolutionary algorithm.
        """
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

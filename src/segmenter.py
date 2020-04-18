from domain import *


class Segmenter:
    def __init__(self, optimiser_param):

        self.optimiser = gradient_descent

        self.optimiser_param = optimiser_param

    def segment(self):

        result_optimiser = self.optimiser(**self.optimiser_param)

        self.w = result_optimiser["w"]

        self.phi = result_optimiser["phi"]

        self.frontier = result_optimiser["frontier"]

        self.norm_grad_w = result_optimiser["norm_grad_w"]

        self.norm_grad_phi = result_optimiser["norm_grad_phi"]

    def plot_stats(self):

        for i in range(self.phi.shape[0]):
            for j in range(self.phi.shape[1]):
                if self.phi[i, j] > 0:
                    self.phi[i, j] = 1
                else:
                    self.phi[i, j] = 0
        plt.imshow(self.phi)
        plt.title("Frontier de la segmentation")
        plt.show()
        plt.plot(self.norm_grad_w)
        plt.title("Gradient de l'image")
        plt.show()
        plt.plot(self.norm_grad_phi)
        plt.title("Gradient de omega")
        plt.show()

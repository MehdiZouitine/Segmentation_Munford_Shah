import numpy as np
import math
from typing import Union, Tuple, List, Dict
import pandas as pd
from tqdm import tqdm_notebook
from itertools import combinations
import matplotlib.pyplot as plt


EPS = 0.1


def in_shape(img: np.ndarray, pixel: List) -> bool:
    """Short summary:
        function that verifies if a pixel belongs to the image


    Parameters
    ----------
    img : np.ndarray
        Description of parameter `img`.
    pixel : List
        Description of parameter `pixel`.

    Returns
    -------
    bool
        Description of returned object.

    """
    return (
        pixel[0] > -1
        and pixel[0] < img.shape[0]
        and pixel[1] > -1
        and pixel[1] < img.shape[1]
    )


sign = lambda x: math.copysign(1, x)
"""Short summary:

    Fonction that return sign of a real number.

Parameters
----------
x : float
    Description of parameter `x`.

Returns
-------
int
    Description of returned object.

"""


def dl(pixel1: np.ndarray, pixel2: np.ndarray, frontier: List[List]) -> int:

    """Short summary:

        Fonction that compute piece of frontier perimeter.

    Parameters
    ----------
    pixel1 : np.ndarray
        Description of parameter `pixel1`.
    pixel2 : np.ndarray
        Description of parameter `pixel2`.
    frontier : List[List]
        Description of parameter `frontier`.

    Returns
    -------
    int
        Description of returned object.

    """

    if (
        (pixel1 in frontier)
        and (pixel2 in frontier)
        and (pixel1[0] != pixel2[0])
        and (pixel1[1] != pixel2[1])
    ):
        return 1
    return 0


def P(frontier: List[List]) -> int:
    """Short summary:
        Fonction that compute the perimeter of Omega using standard dl

    Parameters
    ----------
    frontier : List[List]
        Description of parameter `frontier`.

    Returns
    -------
    int
        Description of returned object.

    """

    return len(frontier)


def H1(w: np.ndarray, frontier: List[List]) -> float:

    """Short summary:
        Fonction that compute the H1 term in the M-S fonctional.

    Parameters
    ----------
    w : np.ndarray
        Description of parameter `w`.
    frontier : List[List]
        Description of parameter `frontier`.

    Returns
    -------
    float
        Description of returned object.

    """
    s = 0
    image_shape = w.shape
    w = np.pad(w, 1, mode="edge")
    for i in range(image_shape[0]):
        for j in range(image_shape[1]):
            if [i, j] not in frontier:
                partial_x = w[i + 1, j] - w[i, j]
                partial_y = w[i, j + 1] - w[i, j]
                s += partial_x ** 2 + partial_y ** 2
    return s


def norm(w: np.ndarray, u: np.ndarray) -> float:
    """Short summary:
        Fonction that compute the last term of M-S fonctional.

    Parameters
    ----------
    w : np.ndarray
        Description of parameter `w`.
    u : np.ndarray
        Description of parameter `u`.

    Returns
    -------
    float
        Description of returned object.

    """

    return np.linalg.norm(w - u) ** 2


def munford_shah(w: np.ndarray, u: np.ndarray, frontier: List[List]) -> float:

    """Short summary:
        Fonction that compute de M-F fonctional

    Parameters
    ----------
    w : np.ndarray
        Description of parameter `w`.
    u : np.ndarray
        Description of parameter `u`.
    frontier : List[List]
        Description of parameter `frontier`.

    Returns
    -------
    float
        Description of returned object.

    """

    return P(frontier) + H1(w, frontier) + norm(w, -u)


def dl2(
    pixel1: np.ndarray,
    pixel2: np.ndarray,
    frontier: List[tuple],
    w: np.ndarray,
    dx: np.ndarray,
    dy: np.ndarray,
) -> float:
    """Short summary:

       Fonction that compute piece of frontier perimeter with the contribution of the gradient of w.

    Parameters
    ----------
    pixel1 : np.ndarray
        Description of parameter `pixel1`.
    pixel2 : np.ndarray
        Description of parameter `pixel2`.
    frontier : List[tuple]
        Description of parameter `frontier`.
    w : np.ndarray
        Description of parameter `w`.
    dx : np.ndarray
        Description of parameter `dx`.
    dy : np.ndarray
        Description of parameter `dy`.

    Returns
    -------
    float
        Description of returned object.

    """

    partial_x = w[pixel1[0] + 1, pixel1[1]] - w[pixel1[0], pixel1[1]]
    partial_y = w[pixel1[0], pixel1[1] + 1] - w[pixel1[0], pixel1[1]]

    return (np.ones(w.shape) - (dx ** 2 + dy ** 2))[pixel1[0], pixel1[1]]


def H_eps(t: float, eps: float) -> float:

    """Short summary:

        Function that eval H_eps function (see chapter 6).

    Parameters
    ----------
    t : float
        Description of parameter `t`.
    eps : float
        Description of parameter `eps`.

    Returns
    -------
    float
        Description of returned object.

    """

    if t >= eps:
        return 1

    elif t >= -eps and t <= eps:
        return (1 / 2) * (1 + (t / eps) + (1 / math.pi) * math.sin(math.pi * t / eps))

    else:
        return 0


def H_eps_derivative(t: float, eps: float) -> float:

    """Short summary:

        Function that eval H_eps derivative function (see chapter 6).

    Parameters
    ----------
    t : float
        Description of parameter `t`.
    eps : float
        Description of parameter `eps`.

    Returns
    -------
    float
        Description of returned object.

    """

    if t >= eps:
        return 0

    elif t >= -eps and t <= eps:
        return (1 / 2 * eps) * (1 + math.cos(math.pi * t / eps))

    else:
        return 0


def in_frontier(pixel: List, phi: np.ndarray) -> bool:
    """Short summary:

       Fonction that return True if a pixel is in the frontier, else False

    Parameters
    ----------
    pixel : List
        Description of parameter `pixel`.
    phi : np.ndarray
        Description of parameter `phi`.

    Returns
    -------
    bool
        Description of returned object.

    """

    for [i, j] in get_neighbour(pixel, phi):
        if sign(phi[i, j]) == sign(phi[pixel[0], pixel[1]]):
            return False
    return True


def grad_x(img: np.ndarray, adjoint: int) -> np.ndarray:
    """Short summary:

       Fonction that compute the first partial derivative of w.

    Parameters
    ----------
    img : np.ndarray
        Description of parameter `img`.
    adjoint : int
        Description of parameter `adjoint`.

    Returns
    -------
    np.ndarray
        Description of returned object.

    """
    sx, sy = np.shape(img)
    diff_x = np.copy(img)

    if adjoint == 0:
        for x in range(sx):
            if x == sx - 1:
                xnext = 0
            else:
                xnext = x + 1
            for y in range(sy):
                diff_x[x, y] = img[xnext, y] - img[x, y]
    else:
        for x in range(sx):
            if x == 0:
                xprev = sx - 1
            else:
                xprev = x - 1
            for y in range(sy):
                diff_x[x, y] = img[xprev, y] - img[x, y]

    return diff_x


def grad_y(img: np.ndarray, adjoint: int) -> np.ndarray:
    """Short summary:

       Fonction that compute the second partial derivative of w.

    Parameters
    ----------
    img : np.ndarray
        Description of parameter `img`.
    adjoint : int
        Description of parameter `adjoint`.

    Returns
    -------
    np.ndarray
        Description of returned object.

    """
    sx, sy = np.shape(img)
    diff_y = np.copy(img)

    if adjoint == 0:

        for y in range(sy):
            if y == sy - 1:
                ynext = 0
            else:
                ynext = y + 1
            for x in range(sx):
                diff_y[x, y] = img[x, ynext] - img[x, y]
    else:
        for y in range(sy):
            if y == 0:
                yprev = sy - 1
            else:
                yprev = y - 1
            for x in range(sx):
                diff_y[x, y] = img[x, yprev] - img[x, y]

    return diff_y


def grad_w_part(
    w: np.ndarray, u: np.ndarray, lambda_: float, mu: float, phi: np.ndarray,
) -> np.ndarray:

    """Short summary:
       Fonction that compute gradient of w part of the gradient.


    Parameters
    ----------
    w : np.ndarray
        Description of parameter `w`.
    u : np.ndarray
        Description of parameter `u`.
    frontier : List[List]
        Description of parameter `frontier`.
    lambda_ : float
        Description of parameter `lambda_`.
    mu : float
        Description of parameter `mu`.
    phi: np.ndarray
        Description of parameter `phi`.


    Returns
    -------
    np.ndarray
        Description of returned object.

    """
    image_size = w.shape

    data_term = 2 * (w - u)
    tmpx = grad_x(w, 0)
    tmpx1 = grad_x(tmpx, 1)
    tmpy = grad_y(w, 0)
    tmpy1 = grad_y(tmpy, 1)

    grad = 2 * (tmpx1 + tmpy1)

    for i in range(grad.shape[0]):
        for j in range(grad.shape[1]):
            if in_frontier([i, j], phi):
                grad[i, j] = 0

    return lambda_ * grad + mu * data_term


def get_neighbour(pixel: List, img: np.ndarray) -> List[List]:
    """Short summary:
        Fonction that compute the neighborhood of a pixel according to the 4-connexity.

    Parameters
    ----------
    pixel : List
        Description of parameter `pixel`.
    img : np.ndarray
        Description of parameter `img`.

    Returns
    -------
    List[List]
        Description of returned object.

    """

    neighborhood = [
        [pixel[0] + 1, pixel[1]],
        [pixel[0], pixel[1] + 1],
        [pixel[0] - 1, pixel[1]],
        [pixel[0], pixel[1] - 1],
    ]
    real_neighborhood = []
    for elt in neighborhood:
        if in_shape(img, elt):
            real_neighborhood.append(elt)
    return real_neighborhood


def grad_phi_part(
    phi: np.ndarray, w: np.ndarray, omega_frontier: List[List], eps: float
):
    """Short summary:
       Fonction that compute gradient of phi part of the gradient.

    Parameters
    ----------
    phi : np.ndarray
        Description of parameter `phi`.
    w : np.ndarray
        Description of parameter `w`.
    omega_frontier : List[List]
        Description of parameter `omega_frontier`.
    eps : float
        Description of parameter `eps`.

    Returns
    -------
    type
        Description of returned object.

    """
    size = phi.shape
    omega_term = np.zeros(size)
    w = np.pad(w, 1, mode="edge")
    tmpx = grad_x(w, 0)
    tmpx1 = grad_x(tmpx, 1)
    tmpy = grad_y(w, 0)
    tmpy1 = grad_y(tmpy, 1)
    for i in range(size[0]):
        for j in range(size[1]):
            for e in get_neighbour([i, j], phi):
                omega_term[i, j] += (
                    dl2([i, j], e, omega_frontier, w, tmpx1, tmpy1)
                    * H_eps_derivative(phi[i, j], eps)
                    * (1 - 2 * H_eps(phi[e[0], e[1]], eps))
                )

    return omega_term


def get_frontier_phi(omega: List[List], phi: np.ndarray) -> List[List]:
    """Short summary:
       Fonction that compute the frontier of omega.

    Parameters
    ----------
    omega : List[List]
        Description of parameter `omega`.
    phi : np.ndarray
        Description of parameter `phi`.

    Returns
    -------
    List[List]
        Description of returned object.

    """
    frontier = []
    for pixel in omega:
        i = pixel[0]
        j = pixel[1]

        if (
            not in_shape(phi, (i + 1, j))
            or not in_shape(phi, (i, j + 1))
            or not in_shape(phi, (i - 1, j))
            or not in_shape(phi, (i, j - 1))
        ):
            frontier.append([i, j])

        elif (
            sign(phi[i, j]) == -sign(phi[i + 1, j])
            or sign(phi[i, j]) == -sign(phi[i, j + 1])
            or sign(phi[i, j]) == -sign(phi[i - 1, j])
            or sign(phi[i, j]) == -sign(phi[i, j - 1])
        ):
            frontier.append([i, j])
    return frontier


def gradient_descent(
    u: np.ndarray,
    step_w: float,
    step_phi: float,
    eps: float,
    lambda_: float,
    mu: float,
    it: int,
    verbose: bool,
    mode: str,
) -> Dict[str, Union[np.ndarray, List]]:

    """Short summary:

       Function that compute simple gradient descent algorithm.

    Parameters
    ----------
    u : np.ndarray
        Description of parameter `u`.
    step_w : float
        Description of parameter `step_w`.
    step_phi : float
        Description of parameter `step_phi`.
    eps : float
        Description of parameter `eps`.
    lambda_ : float
        Description of parameter `lambda_`.
    mu : float
        Description of parameter `mu`.
    it : int
        Description of parameter `it`.
    verbose : bool
        Description of parameter `verbose`.
    mode : str
        Description of parameter `mode`.

    Returns
    -------
    Dict[str,Union[np.ndarray,List]]
        Description of returned object.

    """

    phi = np.copy(u)
    # phi = np.random.uniform(-1, 1, u.shape)
    omega = np.argwhere(phi >= 0).tolist()
    frontier = get_frontier_phi(omega=omega, phi=phi)
    norm_grad_phi = []
    norm_grad_w = []
    functional = []
    w = u

    if mode == "standard":
        for i in tqdm_notebook(range(it)):
            print(f"itération {i}/{it}")
            grad_w = grad_w_part(w, u, lambda_, mu, phi)
            w = w - (step_w * grad_w)

            grad_phi = grad_phi_part(phi=phi, w=w, omega_frontier=frontier, eps=eps)
            phi = phi - (step_phi * grad_phi)

            omega = np.argwhere(phi >= 0).tolist()
            frontier = get_frontier_phi(omega=omega, phi=phi)

            norm_grad_phi.append(np.linalg.norm(grad_phi))
            norm_grad_w.append(np.linalg.norm(grad_w))
            functional.append(munford_shah(w, u, frontier))
            if verbose:
                print(f"itération {i} : w gradient: {norm_grad_w[-1]}")
                print(f"itération {i} : phi gradient: {norm_grad_phi[-1]}")
                print(f"itération {i} munford_shah functional: {functional[-1]}")

    return {
        "w": w,
        "omega": omega,
        "phi": phi,
        "frontier": frontier,
        "norm_grad_phi": norm_grad_phi,
        "norm_grad_w": norm_grad_w,
        "functional": functional,
    }

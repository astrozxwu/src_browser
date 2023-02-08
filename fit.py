import os
import re

import numpy as np
import scipy.optimize as op

import config

PATH = config.data_path


def load(fn, subs=True, usecols=(0, 1, 2)):
    df = np.loadtxt(fn, usecols=usecols).T
    if subs:
        if df[0][0] > 2450000:
            df[0] = df[0] - 2450000
    return df


def mag2flux(data):
    refmag = 18
    mag = data[1]
    err = data[2]
    flux = 3631 * 10 ** (0.4 * (refmag - mag))
    ferr = flux * err * 0.4 * np.log(10)
    return np.array([data[0], flux, ferr])


def flux2mag(data):
    refmag = 18
    if len(data) == 1:
        return -2.5 * np.log10(data[0] / 3631) + refmag
    flux = data[1]
    ferr = data[2]
    mag = -2.5 * np.log10(flux / 3631) + refmag
    magerr = ferr / flux * 2.5 / np.log(10)
    return np.array([data[0], mag, magerr])


def getchi2_single(dat, model, blending=False, ap=False):
    """
    dat like [fluxes,errors]
    model like [magnifications]
    """
    y = dat[1] / dat[2]
    if ap and blending:
        A = np.vstack([model / dat[2], 1 / dat[2], dat[3] / dat[2]]).T
    elif blending:
        A = np.vstack([model / dat[2], 1 / dat[2]]).T
    elif ap:
        A = np.vstack([model / dat[2], dat[3] / dat[2]]).T
    else:
        A = np.vstack([model / dat[2]]).T
    res = np.linalg.lstsq(A, y, rcond=None)

    f = np.append(res[0], [0, 0])
    if ap and not blending:
        f[2] = f[1]
        f[1] = 0
    return res[1][0], f[:3]


def PSPL(t, t_0, u_0, t_E):
    tau = (t - t_0) / t_E
    u2 = u_0**2 + tau**2
    u = u2**0.5
    return (u2 + 2) / u / (u2 + 4) ** 0.5


def fit(event_name, u_0, t_0, t_E, bl=False):
    try:
        os.chdir(os.path.join(PATH, event_name))
    except:
        return "event folder not found"
    l = os.listdir(".")
    if "KMT" in event_name:
        pattern = "KMT[C][0-9][0-9]_I.pysis"
        files = list(filter(lambda x: re.search(pattern, x) != None, l))
        _usecols = (0, 3, 4)
    elif "Gaia" in event_name:
        pattern = event_name + ".*_(LCOGT|Gaia)-[rigVG].*.txt"
        files = list(filter(lambda x: re.search(pattern, x) != None, l))
        _usecols = (0, 1, 2)
    else:
        return "phot file not found"
    data = [(load(i, usecols=_usecols)) for i in files]
    data = [mag2flux(i) for i in data]

    def chi2(theta):
        t0, tE = theta
        _chi2 = 0
        for i in data:
            model = PSPL(i[0], t0, u_0, tE)
            _chi2 += getchi2_single(i, model, blending=bl)[0]
        return _chi2

    res = op.minimize(chi2, x0=[t_0, t_E])
    t0, tE = res.x
    _bl = 1 if bl else 0
    model_file = f"u0{u_0:.3f}bl{_bl}.model"
    model_par = f"u0{u_0:.3f}bl{_bl}.par"
    ref = 0
    for i in range(len(files)):
        if "Gaia-G" in files[i]:
            ref = i
    flux_ref = data[ref]
    _model = PSPL(flux_ref[0], t0, u_0, tE)
    chi2, f = getchi2_single(flux_ref, _model, blending=bl)
    t = np.concatenate(
        [
            np.linspace(t0 - 2 * tE, t0 - 0.2 * tE, 100),
            np.linspace(t0 - 0.2 * tE, t0 + 0.2 * tE, 100),
            np.linspace(t0 + 0.2 * tE, t0 + 2 * tE, 100),
        ]
    )
    model_mag = flux2mag([PSPL(t, t0, u_0, tE) * f[0] + f[1]])
    np.savetxt(model_file, np.array([t, model_mag]).T, fmt="%12.4f %8.3f")
    np.savetxt(
        model_par,
        np.array([res.fun, t0, u_0, tE, flux2mag([f[0]]), flux2mag([f[1] + f[0]])]),
    )
    return "success"


def loadfit(event_name):
    if event_name not in os.listdir(PATH):
        return {}, []
    path = os.path.join(PATH, event_name)  # PATH + event_name + '/'
    os.chdir(path)
    l = os.listdir(".")

    par_files = list(filter(lambda x: re.search(".+.par", x) is not None, l))
    pars = []
    models = []
    for par in par_files:
        para = np.loadtxt(par)
        model = par.replace("par", "model")
        u0bl = model[:-6]
        bl = 0 if para[5] == 0 else 1
        fit = {
            "u0": para[2],
            "t0": para[1],
            "tE": para[3],
            "Is": para[4],
            "Ib": para[5],
            "bl": bl,
            "chi2": para[0],
            "name": f"{u0bl}",
        }
        df = np.loadtxt(model)
        if df[0][0] < 2450000:
            df = df.T
            df[0] = df[0] + 2450000
            df = df.T
        df = df[df.T[0] > 2459300]
        models.append(
            {"name": f"{u0bl}", "data": df.tolist(), "type": "line", "color": "#000000"}
        )
        pars.append(fit)
    return pars, models

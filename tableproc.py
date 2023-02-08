import os

import astropy.coordinates as coord
import astropy.units as u
import numpy as np
from astropy.table import Table
from astroquery.vizier import Vizier
from astroquery.xmatch import XMatch

import config

keys = [
    "Event",
    "PubDate",
    "TNS",
    "RA",
    "Dec",
    "l",
    "b",
    "t0",
    "u0",
    "tE",
    "Kest",
    "Gmag",
    "Kmag",
    "r_K",
    "gbase",
    "rbase",
    "ibase",
    "G_FT",
    "K_FT",
    "r_FT",
    "G_AO",
    "r_AO",
    "AT",
    "UT",
    "AT_wide",
    "UT_wide",
    "Can",
    "Status",
    "Comment",
    "Tags",
]
dtypes = [
    "S32",
    "S32",
    "S16",
    "S32",
    "S32",
    "f4",
    "f4",
    "f2",
    "f4",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "f2",
    "i4",
    "i4",
    "i4",
    "i4",
    "i4",
    "i4",
    "S128",
    "S128",
]
dvalues = [
    "--",
    "--",
    "--",
    "--",
    "--",
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    99.99,
    0,
    0,
    0,
    0,
    0,
    99.99,
    0,
    99.99,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    "--",
    ";",
]
formatter = {
    "t0": ".2f",
    "u0": ".3f",
    "tE": ".2f",
    "Kest": ".2f",
    "Kmag": ".2f",
    "Gmag": ".2f",
    "r_K": ".2f",
    "gbase": ".2f",
    "rbase": ".2f",
    "ibase": ".2f",
    "G_FT": ".2f",
    "K_FT": ".2f",
    "r_FT": ".2f",
    "G_AO": ".2f",
    "r_AO": ".2f",
}
row_tp = {_k: _v for (_k, _v) in zip(keys, dvalues)}


def get_radec_keys_catalog(catalog):
    if catalog == "gaiadr3":
        v_catalog = "I/355/gaiadr3"
        kwd = ["RA_ICRS", "DE_ICRS"]
    if catalog == "2mass":
        v_catalog = "II/246/out"
        kwd = ["RAJ2000", "DEJ2000"]
    if catalog == "vvv":
        v_catalog = "II/348/vvv2"
        kwd = ["RAJ2000", "DEJ2000"]
    if catalog == "vhs":
        pass
    if catalog == "refcat2":
        v_catalog = "J/ApJ/867/105/refcat2"
        kwd = ["RA_ICRS", "DE_ICRS"]
    return v_catalog, kwd


def query_table(ra_dec, catalog="gaiadr3", radius="30s", column_filters={}):
    """
    ra_dec : in hh:mm:ss format
    """
    if catalog == "gaiadr3":
        v_catalog = "I/355/gaiadr3"
        kwd = ["+_r", "RA_ICRS", "DE_ICRS", "Gmag", "e_Gmag"]
    if catalog == "2mass":
        v_catalog = "II/246/out"
        kwd = ["+_r", "RAJ2000", "DEJ2000", "Kmag", "e_Kmag"]
    if catalog == "vvv":
        v_catalog = "II/348/vvv2"
        kwd = ["+_r", "RAJ2000", "DEJ2000", "Ksmag3", "e_Ksmag3"]
    if catalog == "vhs":
        pass
        # to be done
    if catalog == "refcat2":
        v_catalog = "J/ApJ/867/105/refcat2"
        kwd = ["+_r", "RA_ICRS", "DE_ICRS", "gmag", "imag", "rmag", "Kmag", "e_Kmag"]
    v = Vizier(columns=kwd)
    v.ROW_LIMIT = -1
    res = v.query_region(
        coord.SkyCoord(ra_dec, unit=(u.hourangle, u.deg), frame="icrs"),
        radius=radius,
        catalog=v_catalog,
        column_filters=column_filters,
    )
    try:
        return res[0]
    except:
        return Table(names=kwd[1:])


def cross_match(input_tab, input_cat, match_cat="gaiadr3", max_distance=1):
    _, keys = get_radec_keys_catalog(input_cat)
    v_catalog, _ = get_radec_keys_catalog(match_cat)

    res = XMatch.query(
        cat1=input_tab,
        cat2=f"vizier:{v_catalog}",
        max_distance=max_distance * u.arcsec,
        colRA1=keys[0],
        colDec1=keys[1],
    )
    return res


def get_VLTI_refstars(ra_dec):
    G_FT = query_table(
        ra_dec, catalog="gaiadr3", radius="30s", column_filters={"Gmag": "<15"}
    )
    G_AO = query_table(
        ra_dec, catalog="gaiadr3", radius="1m", column_filters={"Gmag": "<11"}
    )
    if G_AO:
        G_AO.sort("Gmag")
    if not G_FT:
        return G_FT, G_FT, G_AO
    FTs = cross_match(G_FT, input_cat="gaiadr3", match_cat="vvv")
    FTs["Ksmag3"].name = "Kmag"
    FTs["e_Ksmag3"].name = "e_Kmag"
    # print(FTs[['Gmag','Kmag','_r']])
    if len(FTs) == 0:
        FTs = cross_match(G_FT, input_cat="gaiadr3", match_cat="2mass")
    FT_AT = FTs[
        np.logical_and.reduce((FTs["Kmag"] < 9, FTs["Gmag"] < 13, FTs["_r"] > 2))
    ]
    FT_UT = FTs[
        np.logical_and.reduce((FTs["Kmag"] < 11, FTs["Gmag"] < 15, FTs["_r"] > 2))
    ]
    FT_AT.sort("Gmag")
    FT_UT.sort("Gmag")
    return FT_AT, FT_UT, G_AO


def vert(ra, dec):
    def d2t(deg):
        hh = deg // 15
        mm = (deg - hh * 15) // 0.25
        ss = (deg - hh * 15 - mm * 0.25) * 240
        return "%02d" % hh + ":" + "%02d" % mm + ":" + format(ss, ">05.2f")

    flag = 1 if dec > 0 else -1
    ap = "" if dec > 0 else "-"
    return d2t(ra), ap + d2t(15 * dec * flag)


def get_lb(ra_dec):
    cod = coord.SkyCoord(ra_dec, unit=(u.hourangle, u.deg), frame="icrs")
    l, b = cod.galactic.l / u.deg, cod.galactic.b / u.deg
    return l.value, b.value


def get_K_est(I, A_I):
    _I = I - A_I
    _K = _I - 1.4 if _I < 16.5 else _I - 1
    return _K + A_I / 7


def format_table(tab, formatter):
    for i in formatter.keys():
        tab[i].info.format = formatter[i]


def vlti_info(ra_dec):
    row = {}
    gri = query_table(ra_dec, catalog="refcat2", radius="1s")
    if gri:
        row["gbase"] = gri[0]["gmag"]
        row["rbase"] = gri[0]["rmag"]
        row["ibase"] = gri[0]["imag"]
    G = query_table(ra_dec, catalog="gaiadr3", radius="1s")
    if G:
        row["Gmag"] = G[0]["Gmag"]
    K = query_table(ra_dec, catalog="vvv", radius="1s")
    K_kwd = "Ksmag3"
    if not K:
        K = query_table(ra_dec, catalog="2mass", radius="1s")
        K_kwd = "Kmag"
    if K:
        row["Kmag"] = K[0][K_kwd]
        row["r_K"] = K[0]["_r"]
    FT_AT, FT_UT, G_AO = get_VLTI_refstars(ra_dec)

    AT_wide = len(FT_AT)
    UT_wide = len(FT_UT)
    row["AT_wide"] = AT_wide
    row["UT_wide"] = UT_wide
    if UT_wide:
        row["G_FT"] = FT_UT[0]["Gmag"]
        row["K_FT"] = FT_UT[0]["Kmag"]
        row["r_FT"] = FT_UT[0]["_r"]
    if G_AO:
        row["G_AO"] = G_AO[0]["Gmag"]
        row["r_AO"] = G_AO[0]["_r"] * 60
    return row


def gen_gaia_row(
    name, rawcsv=os.path.join(config.data_path, "alerts.csv"), update_raw=False
):
    row = dict(zip(keys, dvalues))
    if update_raw or not os.path.isfile(rawcsv):
        os.system(f"wget http://gsaweb.ast.cam.ac.uk/alerts/alerts.csv -O {rawcsv}")
    df_Gaia = Table.read(rawcsv, format="csv")
    df_Gaia = df_Gaia[df_Gaia["#Name"] == name]
    gaia = df_Gaia.to_pandas().to_dict(orient="records")[0]
    RA, Dec = vert(gaia["RaDeg"], gaia["DecDeg"])
    l, b = get_lb(RA + " " + Dec)
    keep = {
        "#Name": "Event",
        "Published": "PubDate",
        "TNSid": "TNS",
        "Comment": "Comment",
    }
    gaia = {keep[i]: gaia[i] for i in keep.keys()}
    gaia["RA"] = RA
    gaia["Dec"] = Dec
    gaia["l"] = l
    gaia["b"] = b
    vlti = vlti_info(RA + " " + Dec)
    row.update(gaia)
    row.update(vlti)
    return row

# Authors: Eric Larson <larson.eric.d@gmail.com>
#
# License: BSD (3-clause)

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from .. import pick_types, Evoked
from ..io import _BaseRaw
from ..bem import fit_sphere_to_headshape


def _get_data(x, ch_idx):
    """Helper to get the (n_ch, n_times) data array"""
    if isinstance(x, _BaseRaw):
        return x[ch_idx][0]
    elif isinstance(x, Evoked):
        return x.data[ch_idx]


def assert_meg_snr(actual, desired, min_tol, med_tol=500., msg=None):
    """Helper to assert channel SNR of a certain level

    Mostly useful for operations like Maxwell filtering that modify
    MEG channels while leaving EEG and others intact.
    """
    from nose.tools import assert_true
    picks = pick_types(desired.info, meg=True, exclude=[])
    others = np.setdiff1d(np.arange(len(actual.ch_names)), picks)
    if len(others) > 0:  # if non-MEG channels present
        assert_allclose(_get_data(actual, others),
                        _get_data(desired, others), atol=1e-11, rtol=1e-5,
                        err_msg='non-MEG channel mismatch')
    actual_data = _get_data(actual, picks)
    desired_data = _get_data(desired, picks)
    bench_rms = np.sqrt(np.mean(desired_data * desired_data, axis=1))
    error = actual_data - desired_data
    error_rms = np.sqrt(np.mean(error * error, axis=1))
    snrs = bench_rms / error_rms
    # min tol
    snr = snrs.min()
    bad_count = (snrs < min_tol).sum()
    msg = ' (%s)' % msg if msg != '' else msg
    assert_true(bad_count == 0, 'SNR (worst %0.2f) < %0.2f for %s/%s '
                'channels%s' % (snr, min_tol, bad_count, len(picks), msg))
    # median tol
    snr = np.median(snrs)
    assert_true(snr >= med_tol, 'SNR median %0.2f < %0.2f%s'
                % (snr, med_tol, msg))


def assert_dig_allclose(info_py, info_bin):
    # test dig positions
    dig_py = info_py['dig']
    dig_bin = info_bin['dig']
    assert_equal(len(dig_py), len(dig_bin))
    for d_py, d_bin in zip(dig_py, dig_bin):
        raise RuntimeError
    R_bin, o_head_bin, o_dev_bin = fit_sphere_to_headshape(info_bin)
    R_py, o_head_py, o_dev_py = fit_sphere_to_headshape(info_py)
    assert_allclose(R_py, R_bin)
    assert_allclose(o_dev_py, o_dev_bin)
    assert_allclose(o_head_py, o_head_bin)

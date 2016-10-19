#!/usr/bin/env python

from __future__ import division, print_function, absolute_import

import warnings
import numpy as np
from numpy.testing import (run_module_suite, assert_almost_equal,
                           assert_allclose, assert_, assert_equal,
                           assert_raises, dec, assert_array_equal)

import pywt

# Check that float32 and complex64 are preserved.  Other real types get
# converted to float64.
dtypes_in = [np.int8, np.float32, np.float64, np.complex64, np.complex128]
dtypes_out = [np.float64, np.float32, np.float64, np.complex64, np.complex128]


# tolerances used in accuracy comparisons
tol_single = 1e-6
tol_double = 1e-13
dtypes_and_tolerances = [(np.float32, tol_single), (np.float64, tol_double),
                         (np.int8, tol_double), (np.complex64, tol_single),
                         (np.complex128, tol_double)]


# determine which wavelets to test
wavelist = pywt.wavelist()
if 'dmey' in wavelist:
    # accuracy is very low for dmey, so omit it
    wavelist.remove('dmey')
# removing wavelets with dwt_possible == False
del_list = []
for wavelet in wavelist:
    if not isinstance(pywt.DiscreteContinuousWavelet(wavelet), pywt.Wavelet):
        del_list.append(wavelet)
for del_ind in del_list:
    wavelist.remove(del_ind)


####
# 1d multilevel dwt tests
####

def test_wavedec():
    x = [3, 7, 1, 1, -2, 5, 4, 6]
    db1 = pywt.Wavelet('db1')
    cA3, cD3, cD2, cD1 = pywt.wavedec(x, db1)
    assert_almost_equal(cA3, [8.83883476])
    assert_almost_equal(cD3, [-0.35355339])
    assert_allclose(cD2, [4., -3.5])
    assert_allclose(cD1, [-2.82842712, 0, -4.94974747, -1.41421356])
    assert_(pywt.dwt_max_level(len(x), db1) == 3)


def test_waverec_invalid_inputs():
    # input must be list or tuple
    assert_raises(ValueError, pywt.waverec, np.ones(8), 'haar')

    # input list cannot be empty
    assert_raises(ValueError, pywt.waverec, [], 'haar')


def test_waverec_accuracies():
    rstate = np.random.RandomState(1234)
    x0 = rstate.randn(8)
    for dt, tol in dtypes_and_tolerances:
        x = x0.astype(dt)
        if np.iscomplexobj(x):
            x += 1j*rstate.randn(8).astype(x.real.dtype)
        coeffs = pywt.wavedec(x, 'db1')
        assert_allclose(pywt.waverec(coeffs, 'db1'), x, atol=tol, rtol=tol)


def test_waverec_none():
    x = [3, 7, 1, 1, -2, 5, 4, 6]
    coeffs = pywt.wavedec(x, 'db1')

    # set some coefficients to None
    coeffs[2] = None
    coeffs[0] = None
    assert_(pywt.waverec(coeffs, 'db1').size, len(x))


def test_waverec_odd_length():
    x = [3, 7, 1, 1, -2, 5]
    coeffs = pywt.wavedec(x, 'db1')
    assert_allclose(pywt.waverec(coeffs, 'db1'), x, rtol=1e-12)


def test_waverec_complex():
    x = np.array([3, 7, 1, 1, -2, 5, 4, 6])
    x = x + 1j
    coeffs = pywt.wavedec(x, 'db1')
    assert_allclose(pywt.waverec(coeffs, 'db1'), x, rtol=1e-12)


def test_multilevel_dtypes_1d():
    # only checks that the result is of the expected type
    wavelet = pywt.Wavelet('haar')
    for dt_in, dt_out in zip(dtypes_in, dtypes_out):
        # wavedec, waverec
        x = np.ones(8, dtype=dt_in)
        errmsg = "wrong dtype returned for {0} input".format(dt_in)

        coeffs = pywt.wavedec(x, wavelet, level=2)
        for c in coeffs:
            assert_(c.dtype == dt_out, "wavedec: " + errmsg)
        x_roundtrip = pywt.waverec(coeffs, wavelet)
        assert_(x_roundtrip.dtype == dt_out, "waverec: " + errmsg)


def test_waverec_all_wavelets_modes():
    # test 2D case using all wavelets and modes
    rstate = np.random.RandomState(1234)
    r = rstate.randn(80)
    for wavelet in wavelist:
        for mode in pywt.Modes.modes:
            coeffs = pywt.wavedec(r, wavelet, mode=mode)
            assert_allclose(pywt.waverec(coeffs, wavelet, mode=mode),
                            r, rtol=tol_single, atol=tol_single)

####
# 1d multilevel swt tests
####


def test_swt_decomposition():
    x = [3, 7, 1, 3, -2, 6, 4, 6]
    db1 = pywt.Wavelet('db1')
    (cA3, cD3), (cA2, cD2), (cA1, cD1) = pywt.swt(x, db1, level=3)
    expected_cA1 = [7.07106781, 5.65685425, 2.82842712, 0.70710678,
                    2.82842712, 7.07106781, 7.07106781, 6.36396103]
    assert_allclose(cA1, expected_cA1)
    expected_cD1 = [-2.82842712, 4.24264069, -1.41421356, 3.53553391,
                    -5.65685425, 1.41421356, -1.41421356, 2.12132034]
    assert_allclose(cD1, expected_cD1)
    expected_cA2 = [7, 4.5, 4, 5.5, 7, 9.5, 10, 8.5]
    assert_allclose(cA2, expected_cA2, rtol=tol_double)
    expected_cD2 = [3, 3.5, 0, -4.5, -3, 0.5, 0, 0.5]
    assert_allclose(cD2, expected_cD2, rtol=tol_double, atol=1e-14)
    expected_cA3 = [9.89949494, ] * 8
    assert_allclose(cA3, expected_cA3)
    expected_cD3 = [0.00000000, -3.53553391, -4.24264069, -2.12132034,
                    0.00000000, 3.53553391, 4.24264069, 2.12132034]
    assert_allclose(cD3, expected_cD3)

    # level=1, start_level=1 decomposition should match level=2
    res = pywt.swt(cA1, db1, level=1, start_level=1)
    cA2, cD2 = res[0]
    assert_allclose(cA2, expected_cA2, rtol=tol_double)
    assert_allclose(cD2, expected_cD2, rtol=tol_double, atol=1e-14)

    coeffs = pywt.swt(x, db1)
    assert_(len(coeffs) == 3)
    assert_(pywt.swt_max_level(len(x)) == 3)


def test_swt_axis():
    x = [3, 7, 1, 3, -2, 6, 4, 6]

    db1 = pywt.Wavelet('db1')
    (cA2, cD2), (cA1, cD1) = pywt.swt(x, db1, level=2)

    # test cases use 2D arrays based on tiling x along an axis and then
    # calling swt along the other axis.
    for order in ['C', 'F']:
        # test SWT of 2D data along default axis (-1)
        x_2d = np.asarray(x).reshape((-1, 1))
        x_2d = np.stack((x, )*5, axis=0)
        if order == 'C':
            x_2d = np.ascontiguousarray(x_2d)
        elif order == 'F':
            x_2d = np.asfortranarray(x_2d)
        (cA2_2d, cD2_2d), (cA1_2d, cD1_2d) = pywt.swt(x_2d, db1, level=2)

        for c in [cA2_2d, cD2_2d, cA1_2d, cD1_2d]:
            assert_(c.shape == x_2d.shape)
        # each row should match the 1D result
        for row in cA1_2d:
            assert_array_equal(row, cA1)
        for row in cA2_2d:
            assert_array_equal(row, cA2)
        for row in cD1_2d:
            assert_array_equal(row, cD1)
        for row in cD2_2d:
            assert_array_equal(row, cD2)

        # test SWT of 2D data along other axis (0)
        x_2d = np.asarray(x).reshape((1, -1))
        x_2d = np.stack((x, )*5, axis=1)
        if order == 'C':
            x_2d = np.ascontiguousarray(x_2d)
        elif order == 'F':
            x_2d = np.asfortranarray(x_2d)
        (cA2_2d, cD2_2d), (cA1_2d, cD1_2d) = pywt.swt(x_2d, db1, level=2,
                                                      axis=0)

        for c in [cA2_2d, cD2_2d, cA1_2d, cD1_2d]:
            assert_(c.shape == x_2d.shape)
        # each column should match the 1D result
        for row in cA1_2d.transpose((1, 0)):
            assert_array_equal(row, cA1)
        for row in cA2_2d.transpose((1, 0)):
            assert_array_equal(row, cA2)
        for row in cD1_2d.transpose((1, 0)):
            assert_array_equal(row, cD1)
        for row in cD2_2d.transpose((1, 0)):
            assert_array_equal(row, cD2)


def test_swt_iswt_integration():
    # This function performs a round-trip swt/iswt transform test on
    # all available types of wavelets in PyWavelets - except the
    # 'dmey' wavelet. The latter has been excluded because it does not
    # produce very precise results. This is likely due to the fact
    # that the 'dmey' wavelet is a discrete approximation of a
    # continuous wavelet. All wavelets are tested up to 3 levels. The
    # test validates neither swt or iswt as such, but it does ensure
    # that they are each other's inverse.

    max_level = 3
    wavelets = pywt.wavelist()
    if 'dmey' in wavelets:
        # The 'dmey' wavelet seems to be a bit special - disregard it for now
        wavelets.remove('dmey')
    for current_wavelet_str in wavelets:
        current_wavelet = pywt.DiscreteContinuousWavelet(current_wavelet_str)
        if isinstance(current_wavelet, pywt.Wavelet):
            input_length_power = int(np.ceil(np.log2(max(
                current_wavelet.dec_len,
                current_wavelet.rec_len))))
            input_length = 2**(input_length_power + max_level - 1)
            X = np.arange(input_length)
            coeffs = pywt.swt(X, current_wavelet, max_level)
            Y = pywt.iswt(coeffs, current_wavelet)
            assert_allclose(Y, X, rtol=1e-5, atol=1e-7)


def test_swt_dtypes():
    wavelet = pywt.Wavelet('haar')
    for dt_in, dt_out in zip(dtypes_in, dtypes_out):
        errmsg = "wrong dtype returned for {0} input".format(dt_in)

        # swt
        x = np.ones(8, dtype=dt_in)
        (cA2, cD2), (cA1, cD1) = pywt.swt(x, wavelet, level=2)
        assert_(cA2.dtype == cD2.dtype == cA1.dtype == cD1.dtype == dt_out,
                "swt: " + errmsg)

        # swt2
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            x = np.ones((8, 8), dtype=dt_in)
            cA, (cH, cV, cD) = pywt.swt2(x, wavelet, level=1)[0]
            assert_(cA.dtype == cH.dtype == cV.dtype == cD.dtype == dt_out,
                    "swt2: " + errmsg)


def test_swt2_ndim_error():
    x = np.ones(8)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', FutureWarning)
        assert_raises(ValueError, pywt.swt2, x, 'haar', level=1)


def test_swt2_iswt2_integration():
    # This function performs a round-trip swt2/iswt2 transform test on
    # all available types of wavelets in PyWavelets - except the
    # 'dmey' wavelet. The latter has been excluded because it does not
    # produce very precise results. This is likely due to the fact
    # that the 'dmey' wavelet is a discrete approximation of a
    # continuous wavelet. All wavelets are tested up to 3 levels. The
    # test validates neither swt2 or iswt2 as such, but it does ensure
    # that they are each other's inverse.

    max_level = 3
    wavelets = pywt.wavelist()
    if 'dmey' in wavelets:
        # The 'dmey' wavelet seems to be a bit special - disregard it for now
        wavelets.remove('dmey')
    for current_wavelet_str in wavelets:
        current_wavelet = pywt.DiscreteContinuousWavelet(current_wavelet_str)
        if isinstance(current_wavelet, pywt.Wavelet):
            input_length_power = int(np.ceil(np.log2(max(
                current_wavelet.dec_len,
                current_wavelet.rec_len))))
            input_length = 2**(input_length_power + max_level - 1)
            X = np.arange(input_length**2).reshape(input_length, input_length)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                coeffs = pywt.swt2(X, current_wavelet, max_level)
                Y = pywt.iswt2(coeffs, current_wavelet)
            assert_allclose(Y, X, rtol=1e-5, atol=1e-5)

####
# 2d multilevel dwt function tests
####


def test_waverec2_accuracies():
    rstate = np.random.RandomState(1234)
    x0 = rstate.randn(4, 4)
    for dt, tol in dtypes_and_tolerances:
        x = x0.astype(dt)
        if np.iscomplexobj(x):
            x += 1j*rstate.randn(4, 4).astype(x.real.dtype)
        coeffs = pywt.wavedec2(x, 'db1')
        assert_(len(coeffs) == 3)
        assert_allclose(pywt.waverec2(coeffs, 'db1'), x, atol=tol, rtol=tol)


def test_multilevel_dtypes_2d():
    wavelet = pywt.Wavelet('haar')
    for dt_in, dt_out in zip(dtypes_in, dtypes_out):
        # wavedec2, waverec2
        x = np.ones((8, 8), dtype=dt_in)
        errmsg = "wrong dtype returned for {0} input".format(dt_in)
        cA, coeffsD2, coeffsD1 = pywt.wavedec2(x, wavelet, level=2)
        assert_(cA.dtype == dt_out, "wavedec2: " + errmsg)
        for c in coeffsD1:
            assert_(c.dtype == dt_out, "wavedec2: " + errmsg)
        for c in coeffsD2:
            assert_(c.dtype == dt_out, "wavedec2: " + errmsg)
        x_roundtrip = pywt.waverec2([cA, coeffsD2, coeffsD1], wavelet)
        assert_(x_roundtrip.dtype == dt_out, "waverec2: " + errmsg)


@dec.slow
def test_waverec2_all_wavelets_modes():
    # test 2D case using all wavelets and modes
    rstate = np.random.RandomState(1234)
    r = rstate.randn(80, 96)
    for wavelet in wavelist:
        for mode in pywt.Modes.modes:
            coeffs = pywt.wavedec2(r, wavelet, mode=mode)
            assert_allclose(pywt.waverec2(coeffs, wavelet, mode=mode),
                            r, rtol=tol_single, atol=tol_single)


def test_wavedec2_complex():
    data = np.ones((4, 4)) + 1j
    coeffs = pywt.wavedec2(data, 'db1')
    assert_(len(coeffs) == 3)
    assert_allclose(pywt.waverec2(coeffs, 'db1'), data, rtol=1e-12)


def test_wavedec2_invalid_inputs():
    # input array has too few dimensions
    data = np.ones(4)
    assert_raises(ValueError, pywt.wavedec2, data, 'haar')


def test_waverec2_invalid_inputs():
    # input must be list or tuple
    assert_raises(ValueError, pywt.waverec2, np.ones((8, 8)), 'haar')

    # input list cannot be empty
    assert_raises(ValueError, pywt.waverec2, [], 'haar')


def test_waverec2_coeff_shape_mismatch():
    x = np.ones((8, 8))
    coeffs = pywt.wavedec2(x, 'db1')

    # introduce a shape mismatch in the coefficients
    coeffs = list(coeffs)
    coeffs[1] = list(coeffs[1])
    coeffs[1][1] = np.zeros((16, 1))
    assert_raises(ValueError, pywt.waverec2, coeffs, 'db1')


def test_waverec2_odd_length():
    x = np.ones((10, 6))
    coeffs = pywt.wavedec2(x, 'db1')
    assert_allclose(pywt.waverec2(coeffs, 'db1'), x, rtol=1e-12)


def test_waverec2_none_coeffs():
    x = np.arange(24).reshape(6, 4)
    coeffs = pywt.wavedec2(x, 'db1')
    coeffs[1] = (None, None, None)
    assert_(x.shape == pywt.waverec2(coeffs, 'db1').shape)

####
# nd multilevel dwt function tests
####


def test_waverecn():
    rstate = np.random.RandomState(1234)
    # test 1D through 4D cases
    for nd in range(1, 5):
        x = rstate.randn(*(4, )*nd)
        coeffs = pywt.wavedecn(x, 'db1')
        assert_(len(coeffs) == 3)
        assert_allclose(pywt.waverecn(coeffs, 'db1'), x, rtol=tol_double)


def test_waverecn_empty_coeff():
    coeffs = [np.ones((2, 2, 2)), {}, {}]
    assert_equal(pywt.waverecn(coeffs, 'db1').shape, (8, 8, 8))

    assert_equal(pywt.waverecn(coeffs, 'db1').shape, (8, 8, 8))
    coeffs = [np.ones((2, 2, 2)), {}, {'daa': np.ones((4, 4, 4))}]

    coeffs = [np.ones((2, 2, 2)), {}, {}, {'daa': np.ones((8, 8, 8))}]
    assert_equal(pywt.waverecn(coeffs, 'db1').shape, (16, 16, 16))


def test_waverecn_invalid_coeffs():
    # approximation coeffs as None and no valid detail oeffs
    coeffs = [None, {}]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')

    # use of None for a coefficient value
    coeffs = [np.ones((2, 2, 2)), {}, {'daa': None}, ]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')

    # invalid key names in coefficient list
    coeffs = [np.ones((4, 4, 4)), {'daa': np.ones((4, 4, 4)),
                                   'foo': np.ones((4, 4, 4))}]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')

    # mismatched key name lengths
    coeffs = [np.ones((4, 4, 4)), {'daa': np.ones((4, 4, 4)),
                                   'da': np.ones((4, 4, 4))}]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')

    # key name lengths don't match the array dimensions
    coeffs = [[[[1.0]]], {'ad': [[[0.0]]], 'da': [[[0.0]]], 'dd': [[[0.0]]]}]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')

    # input list cannot be empty
    assert_raises(ValueError, pywt.waverecn, [], 'haar')


def test_waverecn_lists():
    # support coefficient arrays specified as lists instead of arrays
    coeffs = [[[1.0]], {'ad': [[0.0]], 'da': [[0.0]], 'dd': [[0.0]]}]
    assert_equal(pywt.waverecn(coeffs, 'db1').shape, (2, 2))


def test_waverecn_invalid_coeffs2():
    # shape mismatch should raise an error
    coeffs = [np.ones((4, 4, 4)), {'ada': np.ones((4, 4))}]
    assert_raises(ValueError, pywt.waverecn, coeffs, 'db1')


def test_wavedecn_invalid_inputs():
    # input array has too few dimensions
    data = np.array(0)
    assert_raises(ValueError, pywt.wavedecn, data, 'haar')

    # invalid number of levels
    data = np.ones(16)
    assert_raises(ValueError, pywt.wavedecn, data, 'haar', level=-1)
    assert_raises(ValueError, pywt.wavedecn, data, 'haar', level=100)


def test_waverecn_accuracies():
    # testing 3D only here
    rstate = np.random.RandomState(1234)
    x0 = rstate.randn(4, 4, 4)
    for dt, tol in dtypes_and_tolerances:
        x = x0.astype(dt)
        if np.iscomplexobj(x):
            x += 1j*rstate.randn(4, 4, 4).astype(x.real.dtype)
        coeffs = pywt.wavedecn(x.astype(dt), 'db1')
        assert_allclose(pywt.waverecn(coeffs, 'db1'), x, atol=tol, rtol=tol)


def test_multilevel_dtypes_nd():
    wavelet = pywt.Wavelet('haar')
    for dt_in, dt_out in zip(dtypes_in, dtypes_out):
        # wavedecn, waverecn
        x = np.ones((8, 8), dtype=dt_in)
        errmsg = "wrong dtype returned for {0} input".format(dt_in)
        cA, coeffsD2, coeffsD1 = pywt.wavedecn(x, wavelet, level=2)
        assert_(cA.dtype == dt_out, "wavedecn: " + errmsg)
        for key, c in coeffsD1.items():
            assert_(c.dtype == dt_out, "wavedecn: " + errmsg)
        for key, c in coeffsD2.items():
            assert_(c.dtype == dt_out, "wavedecn: " + errmsg)
        x_roundtrip = pywt.waverecn([cA, coeffsD2, coeffsD1], wavelet)
        assert_(x_roundtrip.dtype == dt_out, "waverecn: " + errmsg)


def test_wavedecn_complex():
    data = np.ones((4, 4, 4)) + 1j
    coeffs = pywt.wavedecn(data, 'db1')
    assert_allclose(pywt.waverecn(coeffs, 'db1'), data, rtol=1e-12)


def test_waverecn_dtypes():
    x = np.ones((4, 4, 4))
    for dt, tol in dtypes_and_tolerances:
        coeffs = pywt.wavedecn(x.astype(dt), 'db1')
        assert_allclose(pywt.waverecn(coeffs, 'db1'), x, atol=tol, rtol=tol)


@dec.slow
def test_waverecn_all_wavelets_modes():
    # test 2D case using all wavelets and modes
    rstate = np.random.RandomState(1234)
    r = rstate.randn(80, 96)
    for wavelet in wavelist:
        for mode in pywt.Modes.modes:
            coeffs = pywt.wavedecn(r, wavelet, mode=mode)
            assert_allclose(pywt.waverecn(coeffs, wavelet, mode=mode),
                            r, rtol=tol_single, atol=tol_single)


def test_coeffs_to_array():
    # single element list returns the first element
    a_coeffs = [np.arange(8).reshape(2, 4), ]
    arr, arr_slices = pywt.coeffs_to_array(a_coeffs)
    assert_allclose(arr, a_coeffs[0])
    assert_allclose(arr, arr[arr_slices[0]])

    assert_raises(ValueError, pywt.coeffs_to_array, [])
    # invalid second element:  array as in wavedec, but not 1D
    assert_raises(ValueError, pywt.coeffs_to_array, [a_coeffs[0], ] * 2)
    # invalid second element:  tuple as in wavedec2, but not a 3-tuple
    assert_raises(ValueError, pywt.coeffs_to_array, [a_coeffs[0],
                                                     (a_coeffs[0], )])
    # coefficients as None is not supported
    assert_raises(ValueError, pywt.coeffs_to_array, [None, ])
    assert_raises(ValueError, pywt.coeffs_to_array, [a_coeffs,
                                                     (None, None, None)])

    # invalid type for second coefficient list element
    assert_raises(ValueError, pywt.coeffs_to_array, [a_coeffs, None])

    # use an invalid key name in the coef dictionary
    coeffs = [np.array([0]), dict(d=np.array([0]), c=np.array([0]))]
    assert_raises(ValueError, pywt.coeffs_to_array, coeffs)


def test_wavedecn_coeff_reshape_even():
    # verify round trip is correct:
    #   wavedecn - >coeffs_to_array-> array_to_coeffs -> waverecn
    # This is done for wavedec{1, 2, n}
    rng = np.random.RandomState(1234)
    params = {'wavedec': {'d': 1, 'dec': pywt.wavedec, 'rec': pywt.waverec},
              'wavedec2': {'d': 2, 'dec': pywt.wavedec2, 'rec': pywt.waverec2},
              'wavedecn': {'d': 3, 'dec': pywt.wavedecn, 'rec': pywt.waverecn}}
    N = 28
    for f in params:
        x1 = rng.randn(*([N] * params[f]['d']))
        for mode in pywt.Modes.modes:
            for wave in wavelist:
                w = pywt.Wavelet(wave)
                maxlevel = pywt.dwt_max_level(np.min(x1.shape), w.dec_len)
                if maxlevel == 0:
                    continue

                coeffs = params[f]['dec'](x1, w, mode=mode)
                coeff_arr, coeff_slices = pywt.coeffs_to_array(coeffs)
                coeffs2 = pywt.array_to_coeffs(coeff_arr, coeff_slices,
                                               output_format=f)
                x1r = params[f]['rec'](coeffs2, w, mode=mode)

                assert_allclose(x1, x1r, rtol=1e-4, atol=1e-4)


def test_coeffs_to_array_padding():
    rng = np.random.RandomState(1234)
    x1 = rng.randn(32, 32)
    mode = 'symmetric'
    coeffs = pywt.wavedecn(x1, 'db2', mode=mode)

    # padding=None raises a ValueError when tight packing is not possible
    assert_raises(ValueError, pywt.coeffs_to_array, coeffs, padding=None)

    # set padded values to nan
    coeff_arr, coeff_slices = pywt.coeffs_to_array(coeffs, padding=np.nan)
    npad = np.sum(np.isnan(coeff_arr))
    assert_(npad > 0)

    # pad with zeros
    coeff_arr, coeff_slices = pywt.coeffs_to_array(coeffs, padding=0)
    assert_(np.sum(np.isnan(coeff_arr)) == 0)
    assert_(np.sum(coeff_arr == 0) == npad)

    # Haar case with N as a power of 2 can be tightly packed
    coeffs_haar = pywt.wavedecn(x1, 'haar', mode=mode)
    coeff_arr, coeff_slices = pywt.coeffs_to_array(coeffs_haar, padding=None)
    # shape of coeff_arr will match in this case, but not in general
    assert_equal(coeff_arr.shape, x1.shape)


def test_waverecn_coeff_reshape_odd():
    # verify round trip is correct:
    #   wavedecn - >coeffs_to_array-> array_to_coeffs -> waverecn
    rng = np.random.RandomState(1234)
    x1 = rng.randn(35, 33)
    for mode in pywt.Modes.modes:
        for wave in ['haar', ]:
            w = pywt.Wavelet(wave)
            maxlevel = pywt.dwt_max_level(np.min(x1.shape), w.dec_len)
            if maxlevel == 0:
                continue
            coeffs = pywt.wavedecn(x1, w, mode=mode)
            coeff_arr, coeff_slices = pywt.coeffs_to_array(coeffs)
            coeffs2 = pywt.array_to_coeffs(coeff_arr, coeff_slices)
            x1r = pywt.waverecn(coeffs2, w, mode=mode)
            # truncate reconstructed values to original shape
            x1r = x1r[[slice(s) for s in x1.shape]]
            assert_allclose(x1, x1r, rtol=1e-4, atol=1e-4)


def test_array_to_coeffs_invalid_inputs():
    coeffs = pywt.wavedecn(np.ones(2), 'haar')
    arr, arr_slices = pywt.coeffs_to_array(coeffs)

    # empty list of array slices
    assert_raises(ValueError, pywt.array_to_coeffs, arr, [])

    # invalid format name
    assert_raises(ValueError, pywt.array_to_coeffs, arr, arr_slices, 'foo')


if __name__ == '__main__':
    run_module_suite()

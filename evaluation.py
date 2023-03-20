import math
import numpy
import scipy.special as spc
import scipy.fftpack as sff
import scipy.stats as sst

# Whole bunch of freaking tests

def monobit(bin_data: str):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

    The focus of this test is the proportion of zeros and ones for the entire sequence. The purpose of this test is
    to determine whether the number of ones and zeros in a sequence are approximately the same as would be expected
    for a truly random sequence. This test assesses the closeness of the fraction of ones to 1/2, that is the number
    of ones and zeros ina  sequence should be about the same. All subsequent tests depend on this test.

    :param bin_data: a binary string
    :return: the p-value from the test
    """
    count = 0
    # If the char is 0 minus 1, else add 1
    for char in bin_data:
        if char == '0':
            count -= 1
        else:
            count += 1
    # Calculate the p value
    sobs = count / math.sqrt(len(bin_data))
    p_val = spc.erfc(math.fabs(sobs) / math.sqrt(2))
    return p_val


def block_frequency(bin_data, block_size=128):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this tests is the proportion of ones within M-bit blocks. The purpose of this tests is to determine
    whether the frequency of ones in an M-bit block is approximately M/2, as would be expected under an assumption
    of randomness. For block size M=1, this test degenerates to the monobit frequency test.
    :param bin_data: a binary string
    :return: the p-value from the test
    :param block_size: the size of the blocks that the binary sequence is partitioned into
    """
    # Work out the number of blocks, discard the remainder
    num_blocks = math.floor(len(bin_data) / block_size)
    block_start, block_end = 0, block_size
    # Keep track of the proportion of ones per block
    proportion_sum = 0.0
    for i in range(num_blocks):
        # Slice the binary string into a block
        block_data = bin_data[block_start:block_end]
        # Keep track of the number of ones
        ones_count = 0
        for char in block_data:
            if char == '1':
                ones_count += 1
        pi = ones_count / block_size
        proportion_sum += pow(pi - 0.5, 2.0)
        # Update the slice locations
        block_start += block_size
        block_end += block_size
    # Calculate the p-value
    chi_squared = 4.0 * block_size * proportion_sum
    p_val = spc.gammaincc(num_blocks / 2, chi_squared / 2)
    return p_val


def independent_runs(bin_data: str):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this tests if the total number of runs in the sequences, where a run is an uninterrupted sequence
    of identical bits. A run of length k consists of k identical bits and is bounded before and after with a bit of
    the opposite value. The purpose of the runs tests is to determine whether the number of runs of ones and zeros
    of various lengths is as expected for a random sequence. In particular, this tests determines whether the
    oscillation between zeros and ones is either too fast or too slow.
    :param bin_data: a binary string
    :return: the p-value from the test
    """
    ones_count, n = 0, len(bin_data)
    for char in bin_data:
        if char == '1':
            ones_count += 1
    p, vobs = float(ones_count / n), 1
    tau = 2 / math.sqrt(len(bin_data))
    if abs(p - 0.5) > tau:
        return 0.0
    else:
        for i in range(1, n):
            if bin_data[i] != bin_data[i - 1]:
                vobs += 1
        # expected_runs = 1 + 2 * (n - 1) * 0.5 * 0.5
        # print("\t", Colours.Italics + "Observed runs =", vobs, "Expected runs", expected_runs, Colours.End)
        num = abs(vobs - 2.0 * n * p * (1.0 - p))
        den = 2.0 * math.sqrt(2.0 * n) * p * (1.0 - p)
        p_val = spc.erfc(float(num / den))
        return p_val


def longest_runs(bin_data: str):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of the tests is the longest run of ones within M-bit blocks. The purpose of this tests is to determine
    whether the length of the longest run of ones within the tested sequences is consistent with the length of the
    longest run of ones that would be expected in a random sequence. Note that an irregularity in the expected
    length of the longest run of ones implies that there is also an irregularity ub tge expected length of the long
    est run of zeroes. Therefore, only one test is necessary for this statistical tests of randomness
    :param bin_data: a binary string
    :return: the p-value from the test
    """
    if len(bin_data) < 128:
        print("\t", "Not enough data to run test!")
        return -1.0
    elif len(bin_data) < 6272:
        k, m = 3, 8
        v_values = [1, 2, 3, 4]
        pik_values = [0.21484375, 0.3671875, 0.23046875, 0.1875]
    elif len(bin_data) < 75000:
        k, m = 5, 128
        v_values = [4, 5, 6, 7, 8, 9]
        pik_values = [0.1174035788, 0.242955959, 0.249363483,
                      0.17517706, 0.102701071, 0.112398847]
    else:
        k, m = 6, 10000
        v_values = [10, 11, 12, 13, 14, 15, 16]
        pik_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

    # Work out the number of blocks, discard the remainder
    # pik = [0.2148, 0.3672, 0.2305, 0.1875]
    num_blocks = math.floor(len(bin_data) / m)
    frequencies = numpy.zeros(k + 1)
    block_start, block_end = 0, m
    for i in range(num_blocks):
        # Slice the binary string into a block
        block_data = bin_data[block_start:block_end]
        # Keep track of the number of ones
        max_run_count, run_count = 0, 0
        for j in range(0, m):
            if block_data[j] == '1':
                run_count += 1
                max_run_count = max(max_run_count, run_count)
            else:
                max_run_count = max(max_run_count, run_count)
                run_count = 0
        max_run_count = max(max_run_count, run_count)
        if max_run_count < v_values[0]:
            frequencies[0] += 1
        for j in range(k):
            if max_run_count == v_values[j]:
                frequencies[j] += 1
        if max_run_count > v_values[k - 1]:
            frequencies[k] += 1
        block_start += m
        block_end += m
    # print(frequencies)
    chi_squared = 0
    for i in range(len(frequencies)):
        chi_squared += (pow(frequencies[i] - (num_blocks *
                        pik_values[i]), 2.0)) / (num_blocks * pik_values[i])
    p_val = spc.gammaincc(float(k / 2), float(chi_squared / 2))
    return p_val


def matrix_rank(bin_data: str, matrix_size=32):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of the test is the rank of disjoint sub-matrices of the entire sequence. The purpose of this test is
    to check for linear dependence among fixed length sub strings of the original sequence. Note that this test
    also appears in the DIEHARD battery of tests.
    :param bin_data: a binary string
    :return: the p-value from the test
    """
    shape = (matrix_size, matrix_size)
    n = len(bin_data)
    block_size = int(matrix_size * matrix_size)
    num_m = math.floor(n / (matrix_size * matrix_size))
    block_start, block_end = 0, block_size
    # print(q, n, num_m, block_size)

    if num_m > 0:
        max_ranks = [0, 0, 0]
        for im in range(num_m):
            block_data = bin_data[block_start:block_end]
            block = numpy.zeros(len(block_data))
            for i in range(len(block_data)):
                if block_data[i] == '1':
                    block[i] = 1.0
            m = block.reshape(shape)
            ranker = BinaryMatrix(m, matrix_size, matrix_size)
            rank = ranker.compute_rank()
            # print(rank)
            if rank == matrix_size:
                max_ranks[0] += 1
            elif rank == (matrix_size - 1):
                max_ranks[1] += 1
            else:
                max_ranks[2] += 1
            # Update index trackers
            block_start += block_size
            block_end += block_size

        piks = [1.0, 0.0, 0.0]
        for x in range(1, 50):
            piks[0] *= 1 - (1.0 / (2 ** x))
        piks[1] = 2 * piks[0]
        piks[2] = 1 - piks[0] - piks[1]

        chi = 0.0
        for i in range(len(piks)):
            chi += pow((max_ranks[i] - piks[i] * num_m),
                       2.0) / (piks[i] * num_m)
        p_val = math.exp(-chi / 2)
        return p_val
    else:
        return -1.0


def spectral(bin_data: str):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this test is the peak heights in the Discrete Fourier Transform of the sequence. The purpose of
    this test is to detect periodic features (i.e., repetitive patterns that are near each other) in the tested
    sequence that would indicate a deviation from the assumption of randomness. The intention is to detect whether
    the number of peaks exceeding the 95 % threshold is significantly different than 5 %.
    :param bin_data: a binary string
    :return: the p-value from the test
    """
    n = len(bin_data)
    plus_minus_one = []
    for char in bin_data:
        if char == '0':
            plus_minus_one.append(-1)
        elif char == '1':
            plus_minus_one.append(1)
    # Product discrete fourier transform of plus minus one
    s = sff.fft(plus_minus_one)
    modulus = numpy.abs(s[0:n / 2])
    tau = numpy.sqrt(numpy.log(1 / 0.05) * n)
    # Theoretical number of peaks
    count_n0 = 0.95 * (n / 2)
    # Count the number of actual peaks m > T
    count_n1 = len(numpy.where(modulus < tau)[0])
    # Calculate d and return the p value statistic
    d = (count_n1 - count_n0) / numpy.sqrt(n * 0.95 * 0.05 / 4)
    p_val = spc.erfc(abs(d) / numpy.sqrt(2))
    return p_val


def universal(bin_data: str):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this test is the number of bits between matching patterns (a measure that is related to the
    length of a compressed sequence). The purpose of the test is to detect whether or not the sequence can be
    significantly compressed without loss of information. A significantly compressible sequence is considered
    to be non-random. **This test is always skipped because the requirements on the lengths of the binary
    strings are too high i.e. there have not been enough trading days to meet the requirements.
    :param bin_data: a binary string
    :return: the p-value from the test
    """
    # The below table is less relevant for us traders and markets than it is for security people
    n = len(bin_data)
    pattern_size = 5
    if n >= 387840:
        pattern_size = 6
    if n >= 904960:
        pattern_size = 7
    if n >= 2068480:
        pattern_size = 8
    if n >= 4654080:
        pattern_size = 9
    if n >= 10342400:
        pattern_size = 10
    if n >= 22753280:
        pattern_size = 11
    if n >= 49643520:
        pattern_size = 12
    if n >= 107560960:
        pattern_size = 13
    if n >= 231669760:
        pattern_size = 14
    if n >= 496435200:
        pattern_size = 15
    if n >= 1059061760:
        pattern_size = 16

    if 5 < pattern_size < 16:
        # Create the biggest binary string of length pattern_size
        ones = ""
        for i in range(pattern_size):
            ones += "1"

        # How long the state list should be
        num_ints = int(ones, 2)
        vobs = numpy.zeros(num_ints + 1)

        # Keeps track of the blocks, and whether were are initializing or summing
        num_blocks = math.floor(n / pattern_size)
        init_bits = 10 * pow(2, pattern_size)
        test_bits = num_blocks - init_bits

        # These are the expected values assuming randomness (uniform)
        c = 0.7 - 0.8 / pattern_size + \
            (4 + 32 / pattern_size) * pow(test_bits, -3 / pattern_size) / 15
        variance = [0, 0, 0, 0, 0, 0, 2.954, 3.125, 3.238, 3.311,
                    3.356, 3.384, 3.401, 3.410, 3.416, 3.419, 3.421]
        expected = [0, 0, 0, 0, 0, 0, 5.2177052, 6.1962507, 7.1836656, 8.1764248, 9.1723243,
                    10.170032, 11.168765, 12.168070, 13.167693, 14.167488, 15.167379]
        sigma = c * math.sqrt(variance[pattern_size] / test_bits)

        cumsum = 0.0
        for i in range(num_blocks):
            block_start = i * pattern_size
            block_end = block_start + pattern_size
            block_data = bin_data[block_start: block_end]
            # Work out what state we are in
            int_rep = int(block_data, 2)

            # Initialize the state list
            if i < init_bits:
                vobs[int_rep] = i + 1
            else:
                initial = vobs[int_rep]
                vobs[int_rep] = i + 1
                cumsum += math.log(i - initial + 1, 2)

        # Calculate the statistic
        phi = float(cumsum / test_bits)
        stat = abs(phi - expected[pattern_size]) / \
            (float(math.sqrt(2)) * sigma)
        p_val = spc.erfc(stat)
        return p_val
    else:
        return -1.0


def berlekamp_massey_algorithm(block_data: str):
    """
    An implementation of the Berlekamp Massey Algorithm. Taken from Wikipedia [1]
    [1] - https://en.wikipedia.org/wiki/Berlekamp-Massey_algorithm
    The Berlekamp–Massey algorithm is an algorithm that will find the shortest linear feedback shift register (LFSR)
    for a given binary output sequence. The algorithm will also find the minimal polynomial of a linearly recurrent
    sequence in an arbitrary field. The field requirement means that the Berlekamp–Massey algorithm requires all
    non-zero elements to have a multiplicative inverse.
    :param block_data:
    :return:
    """
    n = len(block_data)
    c = numpy.zeros(n)
    b = numpy.zeros(n)
    c[0], b[0] = 1, 1
    l, m, i = 0, -1, 0
    int_data = [int(el) for el in block_data]
    while i < n:
        v = int_data[(i - l):i]
        v = v[::-1]
        cc = c[1:l + 1]
        d = (int_data[i] + numpy.dot(v, cc)) % 2
        if d == 1:
            temp = copy.copy(c)
            p = numpy.zeros(n)
            for j in range(0, l):
                if b[j] == 1:
                    p[j + i - m] = 1
            c = (c + p) % 2
            if l <= 0.5 * i:
                l = i + 1 - l
                m = i
                b = temp
        i += 1
    return l


def linear_complexity(bin_data: str, block_size=500):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this test is the length of a linear feedback shift register (LFSR). The purpose of this test is to
    determine whether or not the sequence is complex enough to be considered random. Random sequences are
    characterized by longer LFSRs. An LFSR that is too short implies non-randomness.
    :param bin_data: a binary string
    :param block_size: the size of the blocks to divide bin_data into. Recommended block_size >= 500
    :return:
    """
    dof = 6
    piks = [0.01047, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]

    t2 = (block_size / 3.0 + 2.0 / 9) / 2 ** block_size
    mean = 0.5 * block_size + (1.0 / 36) * (9 + (-1) ** (block_size + 1)) - t2

    num_blocks = int(len(bin_data) / block_size)
    if num_blocks > 1:
        block_end = block_size
        block_start = 0
        blocks = []
        for i in range(num_blocks):
            blocks.append(bin_data[block_start:block_end])
            block_start += block_size
            block_end += block_size

        complexities = []
        for block in blocks:
            complexities.append(berlekamp_massey_algorithm(block))

        t = ([-1.0 * (((-1) ** block_size) * (chunk - mean) + 2.0 / 9)
             for chunk in complexities])
        vg = numpy.histogram(
            t, bins=[-9999999999, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 9999999999])[0][::-1]
        im = ([((vg[ii] - num_blocks * piks[ii]) ** 2) /
              (num_blocks * piks[ii]) for ii in range(7)])

        chi_squared = 0.0
        for i in range(len(piks)):
            chi_squared += im[i]
        p_val = spc.gammaincc(dof / 2.0, chi_squared / 2.0)
        return p_val
    else:
        return -1.0


def serial(bin_data: str, pattern_length=16, method="first"):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this test is the frequency of all possible overlapping m-bit patterns across the entire
    sequence. The purpose of this test is to determine whether the number of occurrences of the 2m m-bit
    overlapping patterns is approximately the same as would be expected for a random sequence. Random
    sequences have uniformity; that is, every m-bit pattern has the same chance of appearing as every other
    m-bit pattern. Note that for m = 1, the Serial test is equivalent to the Frequency test of Section 2.1.
    :param bin_data: a binary string
    :param pattern_length: the length of the pattern (m)
    :return: the P value
    """
    n = len(bin_data)
    # Add first m-1 bits to the end
    bin_data += bin_data[:pattern_length - 1:]

    # Get max length one patterns for m, m-1, m-2
    max_pattern = ''
    for i in range(pattern_length + 1):
        max_pattern += '1'

    # Keep track of each pattern's frequency (how often it appears)
    vobs_one = numpy.zeros(int(max_pattern[0:pattern_length:], 2) + 1)
    vobs_two = numpy.zeros(int(max_pattern[0:pattern_length - 1:], 2) + 1)
    vobs_thr = numpy.zeros(int(max_pattern[0:pattern_length - 2:], 2) + 1)

    for i in range(n):
        # Work out what pattern is observed
        vobs_one[int(bin_data[i:i + pattern_length:], 2)] += 1
        vobs_two[int(bin_data[i:i + pattern_length - 1:], 2)] += 1
        vobs_thr[int(bin_data[i:i + pattern_length - 2:], 2)] += 1

    vobs = [vobs_one, vobs_two, vobs_thr]
    sums = numpy.zeros(3)
    for i in range(3):
        for j in range(len(vobs[i])):
            sums[i] += pow(vobs[i][j], 2)
        sums[i] = (sums[i] * pow(2, pattern_length - i) / n) - n

    # Calculate the test statistics and p values
    del1 = sums[0] - sums[1]
    del2 = sums[0] - 2.0 * sums[1] + sums[2]
    p_val_one = spc.gammaincc(pow(2, pattern_length - 1) / 2, del1 / 2.0)
    p_val_two = spc.gammaincc(pow(2, pattern_length - 2) / 2, del2 / 2.0)

    # For checking the outputs
    if method == "first":
        return p_val_one
    elif method == "both":
        return p_val_one, p_val_two
    else:
        # I am not sure if this is correct, but it makes sense to me.
        return min(p_val_one, p_val_two)


def approximate_entropy(bin_data: str, pattern_length=10):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    As with the Serial test of Section 2.11, the focus of this test is the frequency of all possible overlapping
    m-bit patterns across the entire sequence. The purpose of the test is to compare the frequency of overlapping
    blocks of two consecutive/adjacent lengths (m and m+1) against the expected result for a random sequence.
    :param bin_data: a binary string
    :param pattern_length: the length of the pattern (m)
    :return: the P value
    """
    n = len(bin_data)
    # Add first m+1 bits to the end
    # NOTE: documentation says m-1 bits but that doesnt make sense, or work.
    bin_data += bin_data[:pattern_length + 1:]

    # Get max length one patterns for m, m-1, m-2
    max_pattern = ''
    for i in range(pattern_length + 2):
        max_pattern += '1'

    # Keep track of each pattern's frequency (how often it appears)
    vobs_one = numpy.zeros(int(max_pattern[0:pattern_length:], 2) + 1)
    vobs_two = numpy.zeros(int(max_pattern[0:pattern_length + 1:], 2) + 1)

    for i in range(n):
        # Work out what pattern is observed
        vobs_one[int(bin_data[i:i + pattern_length:], 2)] += 1
        vobs_two[int(bin_data[i:i + pattern_length + 1:], 2)] += 1

    # Calculate the test statistics and p values
    vobs = [vobs_one, vobs_two]
    sums = numpy.zeros(2)
    for i in range(2):
        for j in range(len(vobs[i])):
            if vobs[i][j] > 0:
                sums[i] += vobs[i][j] * math.log(vobs[i][j] / n)
    sums /= n
    ape = sums[0] - sums[1]
    chi_squared = 2.0 * n * (math.log(2) - ape)
    p_val = spc.gammaincc(pow(2, pattern_length - 1), chi_squared / 2.0)
    return p_val


def cumulative_sums(bin_data: str, method="forward"):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    The focus of this test is the maximal excursion (from zero) of the random walk defined by the cumulative sum of
    adjusted (-1, +1) digits in the sequence. The purpose of the test is to determine whether the cumulative sum of
    the partial sequences occurring in the tested sequence is too large or too small relative to the expected
    behavior of that cumulative sum for random sequences. This cumulative sum may be considered as a random walk.
    For a random sequence, the excursions of the random walk should be near zero. For certain types of non-random
    sequences, the excursions of this random walk from zero will be large.
    :param bin_data: a binary string
    :param method: the method used to calculate the statistic
    :return: the P-value
    """
    n = len(bin_data)
    counts = numpy.zeros(n)
    # Calculate the statistic using a walk forward
    if method != "forward":
        bin_data = bin_data[::-1]

    ix = 0
    for char in bin_data:
        sub = 1
        if char == '0':
            sub = -1
        if ix > 0:
            counts[ix] = counts[ix - 1] + sub
        else:
            counts[ix] = sub
        ix += 1

    # This is the maximum absolute level obtained by the sequence
    abs_max = numpy.max(numpy.abs(counts))

    start = int(numpy.floor(0.25 * numpy.floor(-n / abs_max) + 1))
    end = int(numpy.floor(0.25 * numpy.floor(n / abs_max) - 1))
    terms_one = []
    for k in range(start, end + 1):
        sub = sst.norm.cdf((4 * k - 1) * abs_max / numpy.sqrt(n))
        terms_one.append(sst.norm.cdf(
            (4 * k + 1) * abs_max / numpy.sqrt(n)) - sub)

    start = int(numpy.floor(0.25 * numpy.floor(-n / abs_max - 3)))
    end = int(numpy.floor(0.25 * numpy.floor(n / abs_max) - 1))
    terms_two = []
    for k in range(start, end + 1):
        sub = sst.norm.cdf((4 * k + 1) * abs_max / numpy.sqrt(n))
        terms_two.append(sst.norm.cdf(
            (4 * k + 3) * abs_max / numpy.sqrt(n)) - sub)

    p_val = 1.0 - numpy.sum(numpy.array(terms_one))
    p_val += numpy.sum(numpy.array(terms_two))
    return p_val


def fitness(sequence):
    # 1. monobit test
    monobit_test = int(monobit(sequence) > 0.01)

    # 2. block frequency test
    block_freq_test = int(block_frequency(sequence) > 0.01)

    # 3. independent_runs test
    runs_test = int(independent_runs(sequence) > 0.01)

    # 4. longest run
    longest_runs_test = int(longest_runs(sequence) > 0.01)

    # 5. matrix_rank
    matrix_rank_test = int(matrix_rank(sequence) > 0.01)

    # 6. spectral
    # spectral_test = int(spectral(sequence) > 0.01)

    # 7. universal
    universal_test = int(universal(sequence) > 0.01)

    # 8. linear_complexity
    linear_complexity_test = int(linear_complexity(sequence) > 0.01)

    # 9. serial
    serial_test = int(serial(sequence) > 0.01)

    # 10. approximate_entropy
    approximate_entropy_test = int(approximate_entropy(sequence) > 0.01)

    # 11. cumulative_sums
    cumulative_sums_test = int(cumulative_sums(sequence) > 0.01)

    result = monobit_test + block_freq_test + matrix_rank_test
    # spectral has numpy issue, runs_test + longest_runs_test need multiple runs
    # result += spectral_test + runs_test + longest_runs_test
    result += universal_test + linear_complexity_test + serial_test
    result += approximate_entropy_test + cumulative_sums_test

    return result

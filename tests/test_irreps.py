import numpy as np

from spgrep.core import (
    get_spacegroup_irreps,
    get_spacegroup_irreps_from_primitive_symmetry,
)
from spgrep.group import (
    get_cayley_table,
    get_factor_system_from_little_group,
    get_little_group,
)
from spgrep.irreps import (
    get_irreps_from_regular,
    get_irreps_from_solvable_group_chain,
    is_equivalent_irrep,
)
from spgrep.representation import (
    get_character,
    get_intertwiner,
    get_regular_representation,
    is_projective_representation,
    is_unitary,
)
from spgrep.transform import transform_symmetry_and_kpoint, unique_primitive_symmetry
from spgrep.utils import (
    NDArrayComplex,
    NDArrayFloat,
    NDArrayInt,
    ndarray2d_to_integer_tuple,
)


def test_get_character(C3v):
    reg = get_regular_representation(C3v)
    actual = get_character(reg)
    expect = np.array([6, 0, 0, 0, 0, 0])
    assert np.allclose(actual, expect)


def test_get_irreps_C3v(C3v):
    reg = get_regular_representation(C3v)
    table = get_cayley_table(C3v)
    irreps = get_irreps_from_regular(
        reg=reg.astype(np.cdouble),
    )
    # Check dimensions
    assert [irrep.shape[1] for irrep in irreps] == [1, 1, 2]
    # Check characters
    characters_expect = np.array(
        [
            [1, 1, 1, 1, 1, 1],  # A1
            [1, 1, 1, -1, -1, -1],  # A2
            [2, -1, -1, 0, 0, 0],  # E
        ]
    )
    characters_actual = np.array([get_character(irrep) for irrep in irreps])
    assert np.allclose(characters_actual, characters_expect)

    for irrep in irreps:
        assert is_unitary(irrep)

    # G0 = {0}
    # G1 = {0, 1, 2}
    # G2 = {0, 1, 2, 3, 4, 5}
    factor_system = np.ones((6, 6), dtype=np.complex_)
    irreps2 = get_irreps_from_solvable_group_chain(
        table,
        factor_system,
        solvable_chain_generators=[1, 3],
    )
    assert np.sum([irrep.shape[1] ** 2 for irrep in irreps2]) == 6
    for irrep in irreps2:
        assert is_projective_representation(irrep, table, factor_system)


def test_get_spacegroup_irreps_from_primitive_symmetry_P42mnm(P42mnm):
    rotations, translations = P42mnm
    kpoint = np.array([0, 1 / 2, 0])  # X point
    irreps, mapping_little_group = get_spacegroup_irreps_from_primitive_symmetry(
        rotations, translations, kpoint
    )
    assert len(irreps) == 2
    assert [irrep.shape[1] for irrep in irreps] == [2, 2]

    little_rotations = rotations[mapping_little_group]
    little_translations = translations[mapping_little_group]
    for irrep in irreps:
        assert check_spacegroup_representation(
            little_rotations, little_translations, kpoint, irrep
        )
        assert is_unitary(irrep)


def test_symmetrize_small_representation_P42mnm(P42mnm):
    rotations, translations = P42mnm
    kpoint = np.array([0, 1 / 2, 0])  # X point
    little_rotations, little_translations, _ = get_little_group(rotations, translations, kpoint)
    factor_system = get_factor_system_from_little_group(
        little_rotations, little_translations, kpoint
    )
    table = get_cayley_table(little_rotations)

    # G0 = {0}
    # G1 = {0, 4}
    # G2 = {0, 2, 4, 6}
    # G3 = {0, 1, 2, 3, 4, 5, 6, 7}
    irreps2 = get_irreps_from_solvable_group_chain(
        table,
        factor_system,
        solvable_chain_generators=[4, 2, 1],
    )
    assert np.sum([irrep.shape[1] ** 2 for irrep in irreps2]) == 8
    for irrep in irreps2:
        assert is_projective_representation(irrep, table, factor_system)


def test_get_spacegroup_irreps_from_primitive_symmetry_Ia3d(Ia3d):
    rotations, translations = Ia3d
    kpoint_conv = np.array([0, 1, 0])  # H point in conventional dual

    # TODO: Refactor to function
    # Transform to primitive
    to_primitive = np.array(
        [
            [-1 / 2, 1 / 2, 1 / 2],
            [1 / 2, -1 / 2, 1 / 2],
            [1 / 2, 1 / 2, -1 / 2],
        ]
    )
    primitive_rotations, primitive_translations, primitive_kpoint = transform_symmetry_and_kpoint(
        to_primitive, rotations, translations, kpoint_conv
    )
    primitive_rotations, primitive_translations, mapping = unique_primitive_symmetry(
        primitive_rotations, primitive_translations
    )
    assert primitive_rotations.shape == (48, 3, 3)
    assert primitive_translations.shape == (48, 3)
    kpoint_prim = np.array([1 / 2, -1 / 2, 1 / 2])
    assert np.allclose(primitive_kpoint, kpoint_prim)

    primitive_irreps, mapping_little_group = get_spacegroup_irreps_from_primitive_symmetry(
        rotations=primitive_rotations,
        translations=primitive_translations,
        kpoint=primitive_kpoint,
    )
    # 48 = 2^2 + 2^2 + 2^2 + 6^2
    assert len(primitive_irreps) == 4
    assert [irrep.shape[1] for irrep in primitive_irreps] == [2, 2, 2, 6]

    little_primitive_rotations = primitive_rotations[mapping_little_group]
    little_primitive_translations = primitive_translations[mapping_little_group]
    for irrep in primitive_irreps:
        assert check_spacegroup_representation(
            little_primitive_rotations, little_primitive_translations, primitive_kpoint, irrep
        )
        assert is_unitary(irrep)


def test_symmetrize_small_representation_Ia3d(Ia3d):
    rotations, translations = Ia3d
    kpoint_conv = np.array([0, 1, 0])  # H point in conventional dual

    # Transform to primitive
    to_primitive = np.array(
        [
            [-1 / 2, 1 / 2, 1 / 2],
            [1 / 2, -1 / 2, 1 / 2],
            [1 / 2, 1 / 2, -1 / 2],
        ]
    )
    primitive_rotations, primitive_translations, primitive_kpoint = transform_symmetry_and_kpoint(
        to_primitive, rotations, translations, kpoint_conv
    )
    primitive_rotations, primitive_translations, mapping = unique_primitive_symmetry(
        primitive_rotations, primitive_translations
    )

    little_rotations, little_translations, _ = get_little_group(
        primitive_rotations, primitive_translations, primitive_kpoint
    )
    factor_system = get_factor_system_from_little_group(
        little_rotations, little_translations, primitive_kpoint
    )
    table = get_cayley_table(little_rotations)

    raise NotImplementedError
    chain_generators = []

    irreps2 = get_irreps_from_solvable_group_chain(
        table,
        factor_system,
        solvable_chain_generators=chain_generators,
    )
    assert np.sum([irrep.shape[1] ** 2 for irrep in irreps2]) == 48
    for irrep in irreps2:
        assert is_projective_representation(irrep, table, factor_system)


def test_get_spacegroup_irreps(corundum_cell):
    # Corundum structure, R-3c (No. 167)
    # T point for hR
    kpoint = np.array([0, 1, 1 / 2])
    irreps, rotations, translations, mapping = get_spacegroup_irreps(*corundum_cell, kpoint=kpoint)
    # order=12, 12 = 2^2 + 2^2 + 2^2
    assert len(irreps) == 3
    assert [irrep.shape[1] for irrep in irreps] == [2, 2, 2]
    assert set(mapping) == set(range(36))  # order of little co-group in conventional

    little_rotations = rotations[mapping]
    little_translations = translations[mapping]
    for irrep in irreps:
        assert check_spacegroup_representation(
            little_rotations, little_translations, kpoint, irrep
        )
        assert is_unitary(irrep)


def check_spacegroup_representation(
    little_rotations: NDArrayInt,
    little_translations: NDArrayFloat,
    kpoint: NDArrayFloat,
    rep: NDArrayComplex,
):
    """Check definition of representation. This function works for primitive and conventional cell."""
    little_rotations_int = [ndarray2d_to_integer_tuple(rotation) for rotation in little_rotations]

    # Check if ``rep`` preserves multiplication
    for r1, t1, m1 in zip(little_rotations, little_translations, rep):
        for r2, t2, m2 in zip(little_rotations, little_translations, rep):
            r12 = r1 @ r2
            t12 = r1 @ t2 + t1
            idx = little_rotations_int.index(ndarray2d_to_integer_tuple(r12))
            # little_translations[idx] may differ from t12 by lattice translation.
            m12 = rep[idx] * np.exp(-2j * np.pi * np.dot(kpoint, t12 - little_translations[idx]))

            if not np.allclose(m12, m1 @ m2):
                return False

    return True


def test_intertwiner():
    rep1 = np.array(
        [
            [[1.0 - 0.0j, 0.0 + 0.0j], [0.0 + 0.0j, 1.0 - 0.0j]],
            [[0.0 + 0.0j, 1.0 - 0.0j], [1.0 - 0.0j, 0.0 + 0.0j]],
            [[-0.0 - 1.0j, 0.0 + 0.0j], [0.0 + 0.0j, -0.0 + 1.0j]],
            [[0.0 + 0.0j, -0.0 - 1.0j], [-0.0 + 1.0j, 0.0 + 0.0j]],
        ]
    )
    rep2 = np.array(
        [
            [[1.0 - 0.0j, 0.0 + 0.0j], [0.0 + 0.0j, 1.0 - 0.0j]],
            [[0.0 + 0.0j, 1.0 - 0.0j], [1.0 - 0.0j, 0.0 + 0.0j]],
            [[-0.0 + 1.0j, 0.0 - 0.0j], [0.0 - 0.0j, 0.0 - 1.0j]],
            [[0.0 - 0.0j, -0.0 + 1.0j], [0.0 - 1.0j, 0.0 - 0.0j]],
        ]
    )

    intertwiner = get_intertwiner(rep1, rep2)
    assert is_equivalent_irrep(get_character(rep1), get_character(rep2))
    assert np.allclose(
        np.einsum("kil,lj->kij", rep1, intertwiner),
        np.einsum("il,klj->kij", intertwiner, rep2),
    )

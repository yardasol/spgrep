from __future__ import annotations

import numpy as np
from spglib import get_pointgroup

from spgrep.utils import NDArrayInt, ndarray2d_to_integer_tuple

# List of point groups after applying transformation matrices given by `spglib.get_pointgroup`
# See https://github.com/spglib/spglib/issues/164
# Operations are ordered as same as Table 3.2.3.2 of ITA (2016).
pg_dataset = {
    "1": [[((1, 0, 0), (0, 1, 0), (0, 0, 1))]],
    "-1": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
        ]
    ],
    "2": [
        # unique axis-a
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
        ],
        # unique axis-b
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
        ],
        # unique axis-c
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
        ],
    ],
    "m": [
        # unique axis-a
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ],
        # unique axis-b
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
        ],
        # unique axis-c
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
        ],
    ],
    "2/m": [
        # unique axis-b
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
        ]
    ],
    "222": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
        ]
    ],
    "mm2": [
        # unique axis-a
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
        ],
        # unique axis-b
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ],
        # unique axis-c
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ],
    ],
    "mmm": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ]
    ],
    "4": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
        ]
    ],
    "-4": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
        ]
    ],
    "4/m": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
        ]
    ],
    "422": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
        ]
    ],
    "4mm": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
        ]
    ],
    "-42m": [
        # -42m
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
        ],
        # -4m2
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
        ],
    ],
    "4/mmm": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
        ]
    ],
    "3": [
        # Hexagonal axes
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
        ]
    ],
    "-3": [
        # Hexagonal axes
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, -1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, -1)),
        ]
    ],
    "32": [
        # 312
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, -1)),
        ],
        # 321
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, -1)),
        ],
    ],
    "3m": [
        # 3m1
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, 1)),
        ],
        # 31m
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, 1)),
        ],
    ],
    "-3m": [
        # -31m
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, -1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, 1)),
        ],
        # -3m1
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, -1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, 1)),
        ],
    ],
    "6": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, 1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, 1)),
        ]
    ],
    "-6": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, -1)),
        ]
    ],
    "6/m": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, 1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, -1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, -1)),
        ]
    ],
    "622": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, 1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, -1)),
        ]
    ],
    "6mm": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, 1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, 1)),
        ]
    ],
    "-6m2": [
        # -6m2
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, -1)),
        ],
        # -62m
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, -1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, 1)),
        ],
    ],
    "6/mmm": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, 1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, 1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 1, 0), (0, 0, -1)),
            ((1, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((0, -1, 0), (1, -1, 0), (0, 0, -1)),
            ((-1, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((-1, 1, 0), (0, 1, 0), (0, 0, 1)),
            ((1, 0, 0), (1, -1, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, -1, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (-1, 1, 0), (0, 0, 1)),
        ]
    ],
    "23": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),  # z,x,y
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
        ]
    ],
    "m-3": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, 0, -1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (1, 0, 0), (0, -1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, 1, 0)),
            ((0, -1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, 1, 0), (0, 0, 1), (-1, 0, 0)),
        ]
    ],
    "432": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
            ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((-1, 0, 0), (0, 0, -1), (0, -1, 0)),
            ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
            ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
            ((0, 0, 1), (0, -1, 0), (1, 0, 0)),
            ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
            ((0, 0, -1), (0, -1, 0), (-1, 0, 0)),
        ]
    ],
    "-43m": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((-1, 0, 0), (0, 0, 1), (0, -1, 0)),
            ((-1, 0, 0), (0, 0, -1), (0, 1, 0)),
            ((1, 0, 0), (0, 0, -1), (0, -1, 0)),
            ((0, 0, 1), (0, 1, 0), (1, 0, 0)),
            ((0, 0, 1), (0, -1, 0), (-1, 0, 0)),
            ((0, 0, -1), (0, 1, 0), (-1, 0, 0)),
            ((0, 0, -1), (0, -1, 0), (1, 0, 0)),
        ]
    ],
    "m-3m": [
        [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
            ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((-1, 0, 0), (0, 0, -1), (0, -1, 0)),
            ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
            ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
            ((0, 0, 1), (0, -1, 0), (1, 0, 0)),
            ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
            ((0, 0, -1), (0, -1, 0), (-1, 0, 0)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, 1, 0), (0, 0, -1)),
            ((1, 0, 0), (0, -1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((0, 0, -1), (-1, 0, 0), (0, -1, 0)),
            ((0, 0, -1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, 1), (1, 0, 0), (0, -1, 0)),
            ((0, 0, 1), (-1, 0, 0), (0, 1, 0)),
            ((0, -1, 0), (0, 0, -1), (-1, 0, 0)),
            ((0, 1, 0), (0, 0, -1), (1, 0, 0)),
            ((0, -1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, 1, 0), (0, 0, 1), (-1, 0, 0)),
            ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
            ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
            ((0, 1, 0), (-1, 0, 0), (0, 0, -1)),
            ((-1, 0, 0), (0, 0, -1), (0, 1, 0)),
            ((1, 0, 0), (0, 0, -1), (0, -1, 0)),
            ((1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((-1, 0, 0), (0, 0, 1), (0, -1, 0)),
            ((0, 0, -1), (0, -1, 0), (1, 0, 0)),
            ((0, 0, -1), (0, 1, 0), (-1, 0, 0)),
            ((0, 0, 1), (0, -1, 0), (-1, 0, 0)),
            ((0, 0, 1), (0, 1, 0), (1, 0, 0)),
        ]
    ],
}

# Figure 3.2.1.3 of ITA (2016)
pg_solvable_chain = {
    "1": [],
    "-1": [(("1", 0), 1)],  # -x,-y,-z
    "2": [
        # unique axis-a
        (("1", 0), 1),  # x,-y,-z
        # unique axis-b
        (("1", 0), 1),  # -x,y,-z
        # unique axis-c
        (("1", 0), 1),  # -x,-y,z
    ],
    "m": [
        # unique axis-a
        (("1", 0), 1),  # -x,y,z
        # unique axis-b
        (("1", 0), 1),  # x,-y,z
        # unique axis-c
        (("1", 0), 1),  # x,y,-z
    ],
    "2/m": [
        # unique axis-b
        (("2", 1), 2)  # -x,-y,-z
    ],
    "222": [(("2", 2), 2)],  # -x,y,-z
    "mm2": [
        # unique axis-a
        (("2", 0), 2),  # x,y,-z
        # unique axis-b
        (("2", 1), 2),  # x,y,-z
        # unique axis-c
        (("2", 2), 2),  # x,y,-z
    ],
    "mmm": [(("222", 0), 4)],  # -x,-y,-z
    "4": [(("2", 2), 2)],  # -y,x,z
    "-4": [(("2", 2), 2)],  # y,-x,-z
    "4/m": [(("4", 0), 4)],  # -x,-y,-z
    "422": [(("4", 0), 4)],  # -x,y,-z
    "4mm": [(("4", 0), 4)],  # x,-y,z
    "-42m": [
        # -42m
        (("-4", 0), 4),  # -x,y,-z
        # -4m2
        (("-4", 0), 4),  # x,-y,z
    ],
    "4/mmm": [(("422", 0), 8)],  # -x,-y,-z
    "3": [(("1", 0), 1)],  # -y,x-y,z
    "-3": [(("3", 0), 3)],  # -x,-y,-z
    "32": [
        # 312
        (("3", 0), 3),  # -y,-x,z
        # 321
        (("3", 0), 3),  # y,x,-z
    ],
    "3m": [
        # 3m1
        (("3", 0), 3),  # -y,-x,z
        # 31m
        (("3", 0), 3),  # y,x,z
    ],
    "-3m": [
        # -31m
        (("32", 0), 6),  # -x,-y,-z
        # -3m1
        (("32", 1), 6),  # -x,-y,-z
    ],
    "6": [(("3", 0), 3)],  # -x,-y,z
    "-6": [(("3", 0), 3)],  # x,y,-z
    "6/m": [(("6", 0), 6)],  # -x,-y,-z
    "622": [(("6", 0), 6)],  # y,x,-z
    "6mm": [(("6", 0), 6)],  # -y,-x,z
    "-6m2": [
        # -6m2
        (("-6", 0), 6),  # -y,-x,z
        # -62m
        (("-6", 0), 6),  # y,x,-z
    ],
    "6/mmm": [(("622", 0), 12)],  # -x,-y,-z
    "23": [(("222", 0), 4)],  # z,x,y
    "m-3": [(("23", 0), 12)],  # -x,-y,-z
    "432": [(("23", 0), 12)],  # y,x,-z
    "-43m": [(("23", 0), 12)],  # y,x,z
    "m-3m": [(("432", 0), 24)],  # -x,-y,-z
}


def get_generators(pg_symbol, idx):
    _, _, gens = _get_generators(pg_symbol, idx, [])
    return gens


def _get_generators(pg_symbol, idx, gens):
    if pg_symbol == "1":
        return None, None, gens

    (next_pg_symbol, next_idx), generator = pg_solvable_chain[pg_symbol][idx]
    gens.append(generator)
    # assert pg_dataset[pg_symbol][idx][:generator] == pg_dataset[next_pg_symbol][next_idx]
    return _get_generators(next_pg_symbol, next_idx, gens)


def get_pointgroup_chain_generators(prim_rotations: NDArrayInt) -> list[int]:
    """Calculate generators of given crystallographic point group in primitive basis.
    The returned generators give a normal series whose factor groups are all Abelian.

    Parameters
    ----------
    prim_rotations: (order, 3, 3)

    Returns
    -------
    generators: list[int]
        Let G0 := prim_rotations and G_{i} := G_{i-1} / < generators[i] > (i = 0, 1, ...).
        Then, G_{i} is normal subgroup of G_{i-1} and factor group G_{i-1}/G_{i} is Abelian.
    """
    pg_symbol, _, P = get_pointgroup(prim_rotations)
    Pinv = np.linalg.inv(P)

    # Match given crystallographic point group with standardized ones in primitive basis.
    order = len(prim_rotations)
    for idx, std_rotations in enumerate(pg_dataset[pg_symbol]):
        matched = [ndarray2d_to_integer_tuple(Pinv @ r @ P) for r in prim_rotations]

        success = True
        mapping = [-1 for _ in range(order)]  # s.t. prim_rotations[mapping[i]] == std_rotations[i]
        for i, ri in enumerate(std_rotations):
            try:
                j = matched.index(ri)  # type: ignore
            except ValueError:
                success = False
                break
            mapping[i] = j
        if success:
            generators = get_generators(pg_symbol, idx)
            return [mapping[g] for g in generators]

    ValueError("Failed to match with tabulated point groups.")  # type: ignore

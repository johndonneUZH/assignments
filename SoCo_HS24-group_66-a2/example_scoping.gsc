[
    "sequence",
    ["set", "get_cube_power", 
        ["function", "x", 
            ["power", ["get", "x"], 3]
        ]
    ],
    ["set", "add_cubes", 
        ["function", ["a", "b"],
            ["sequence", 
                ["set", "result", 
                    ["add", 
                        ["call", "get_cube_power", ["get", "a"]],  
                        ["call", "get_cube_power", ["get", "b"]] 
                    ]
                ],
                ["set", "sub",
                    ["function", "z", 
                        ["set", "inner", ["absolute", -1000]]
                    ]
                ],
                ["add", ["get", "result"], ["call", "sub", 32]]
            ]
        ]
    ],
    ["call", "add_cubes", 2, 4]
]
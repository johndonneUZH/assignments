[
    "sequence",
    ["set", "do_my_multiplication", 
        ["function", ["a", "b"], 
            ["multiplication", ["get", "a"], ["get", "b"]]
        ]
    ],  
    ["set", "outer_func", 
        ["function", "x", 
            ["sequence", 
                ["set", "middle_func", 
                    ["function", "y", 
                        ["sequence",
                            ["set", "x", ["add", ["get", "x"], 10]], 
                            ["set", "inner_func", 
                                ["function", [], ["call", "do_my_multiplication", ["get", "x"], ["get", "y"]]]
                            ],
                            ["call", "inner_func"]
                        ]
                    ]
                ],
                ["call", "middle_func", 3]
            ]
        ]
    ],
    ["call", "outer_func", 4]
]
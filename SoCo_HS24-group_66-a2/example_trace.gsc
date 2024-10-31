[
    "sequence",
    ["set", "x", 10],
    ["set", "helper", 
        ["function", ["n"], 
            ["add", ["get", "x"], ["get", "n"]]
        ]
    ],
    ["set", "outer", 
        ["function", ["a"],
            [
                "sequence",
                ["set", "x", 1],
                ["set", "inner",
                    ["function", ["b"],
                        [
                            "sequence",
                            ["set", "x", 2],
                            ["set", "deepHelper",
                                ["function", ["n"],
                                    ["add", 
                                        ["call", "helper", ["get", "n"]], 
                                        ["get", "x"]
                                    ]
                                ]
                            ],
                            ["add",
                                ["call", "helper", ["get", "a"]],
                                ["call", "deepHelper", ["get", "b"]]
                            ]
                        ]
                    ]
                ],
                ["call", "inner", 5]
            ]
        ]
    ],
    ["call", "outer", 3]
]
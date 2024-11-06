[
    "sequence",
    ["set", "x", 10],
    ["set", "helper", 
        ["function", ["n"], 
            ["add", ["get", "x"], ["get", "n"]]
        ]
    ],
    ["set", "mathFunc",
        ["function", ["a", "b"],
            ["sequence",
                ["set", "result1",
                    ["multiplication", ["get", "a"], ["get", "b"]]
                ],
                ["set", "result2",
                    ["division", ["get", "result1"], 2]
                ],
                ["set", "result3",
                    ["power", ["get", "result2"], 2]
                ],
                ["set", "result4",
                    ["absolute", ["substract", ["get", "result3"], 100]]
                ],
                ["get", "result4"]
            ]
        ]
    ],
    [ "set", "nestedCalc",
        ["function", ["a", "b"],
            ["sequence",
                ["set", "temp1", 
                    ["multiplication", ["get", "a"], ["get", "b"]]
                ],
                ["set", "temp2", 
                    ["division", ["get", "temp1"], 2]
                ],
                ["or",
                    ["and", ["get", "temp2"], 1],
                    ["xor", ["get", "a"], ["get", "b"]]
                ]
            ]
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
                                    ["sequence",
                                        ["set", "mathResult",
                                            ["call", "mathFunc", ["get", "n"], ["get", "x"]]
                                        ],
                                        ["add", 
                                            ["call", "helper", ["get", "n"]], 
                                            ["get", "x"]
                                        ]
                                    ]
                                ]
                            ],
                            ["add",
                                ["call", "nestedCalc", ["get", "a"], ["get", "b"]],
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
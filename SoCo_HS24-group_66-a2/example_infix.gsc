[
    "sequence",
    ["set", "calculate", 
        ["function", ["x", "y", "z"], 
            ["sequence", 
                ["set", "result1", "['get', 'x'] + ['get', 'y']"], 
                ["set", "result2", "['get', 'x'] - ['get', 'z']"],     
                ["set", "result3", "['get', 'y'] * ['get', 'z']"],     
                ["set", "result4", "['get', 'x'] / ['get', 'y']"],
                ["set", "logic_or", "['get', 'result1'] or ['get', 'result3']"], 
                ["set", "logic_and", "['get', 'result1'] and ['get', 'result3']"], 
                ["set", "logic_xor", "['get', 'result2'] xor ['get', 'result3']"], 
                "['get', 'result1'] + ['get', 'result4']" 
            ]
        ]
    ],  
    ["call", "calculate", 8, 4, 2]
]
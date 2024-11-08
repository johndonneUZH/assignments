[
    "sequence",
    ["set", "calculate", 
        ["function", ["x", "y", "z"], 
            ["sequence", 
                ["set", "result1", "['['['get', 'x'] * 20'] / 15 '] + ['['get', 'y'] + 23']"],                 
                ["set", "result2", "['get', 'x'] - ['get', 'z']"],     
                ["set", "result3", "['get', 'y'] * ['get', 'z']"],     
                ["set", "result4", "['['get', 'result3'] * 100']/ ['['add', ['get', 'x'], 2] + 2']"],
                ["set", "logic_or", "['get', 'result1'] or ['get', 'result3']"], 
                ["set", "logic_and", "['get', 'result1'] and ['get', 'result3']"], 
                ["set", "logic_xor", "['get', 'result2'] xor ['get', 'result3']"], 
                "['get', 'result1'] + ['get', 'result4']" 
            ]
        ]
    ],  
    ["call", "calculate", 8, 4, 2]
]



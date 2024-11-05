<<<<<<< HEAD
["sequence", 
["set", "x", ["100/ ['['add', 1,2] + 2']"]], 
["set", "y", ["100 / ['add', ['1 and 1'], ['1+1']]"]], 
["set", "z", ["['get', 'x'] + 9"]],
["['get', 'z'] + ['['get', 'y'] + ['get', 'x']']"]
]

=======
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
>>>>>>> 410665b2dd4b7fa7d8c5bc59b988296fa77e87eb

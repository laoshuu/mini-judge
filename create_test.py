# %%
import inspect
import uuid

# %%
# 參數設定
q_num = 8                               # 問題數量
sample_num = 2                           # 不計分 (sample) 測資數量
non_sample_num = 10                      # 計分測資數量
testcase_scores = [2, 2, 2, 2, 2, 2, 2, 2]     # 各題測資配分

# %%
# 將從文件讀出的測資，根據 info.txt 轉換成相應的變數。
def convert_type(vars, var_type):
    for j, var in enumerate(vars):
        if "list" in var_type[j]:   # handle list input
            element_type = eval(var_type[j][var_type[j].find("(") + 1 : var_type[j].find(")")])
            vars[j] = list(map(element_type, var.split(' '))) 
        else:
            if eval(var_type[j]) == bool:
                vars[j] = eval(var) # handle bool input
            else:
                vars[j] = eval(var_type[j])(var) # handle int, str input
    return vars

# %%
def init(q = 1, sample = True):
    # sample or non-sample 的初始化
    if sample:
        testcase_num = sample_num
        fp = 'sample'
    else:
        testcase_num = non_sample_num
        fp = 'testcase'

    # 讀取測資相關資訊（info.txt）
    path = f'./testcase/Q{q}'
    with open(path + f'/Q{q}_info.txt') as file:
        info = file.readlines()
        info = [t.strip() for t in info]
        input_num = int(info[0])
        ans_num = int(info[2])
        input_type = [tp for tp in info[1].split(' ')]
        ans_type = [tp for tp in info[3].split(' ')]
        
        # 讀取測資（sample_XX.txt, testcase_XX.txt）
        params = []
        for i in range(1, testcase_num + 1):
            # with open(path + f'/Q{q}_{fp}_{"0" * (1 - i // 10)}{i}.txt', 'r', encoding="utf-8") as f:
            with open(path + f'/Q{q}_{fp}_0{i}.txt', 'r', encoding="utf-8") as f:
                text = f.readlines()
                text = [t.strip() for t in text]

                inputs, outputs = text[:input_num], text[input_num:]
                inputs = convert_type(inputs, input_type)
                outputs = convert_type(outputs, ans_type)
            params.append({'input': inputs, 'output': outputs})  
    return params


# %%
# 將錯題資訊提供給參賽者，印出錯誤測資及其變數名稱
def map_input(i, var_names, var_vals, ans):
    hint_str = f"input: {var_names[0]} = {var_vals[0]}"
    for i in range(1, len(var_names)):
        hint_str += (f", {var_names[i]} = {var_vals[i]}")
    hint_str += f"\noutput: "
    hint_str += f"{' '.join(map(str, ans))}"
    return hint_str

# %%
class Problem:
    def __init__(self, id):
        self.id = id
        self.sample = init(self.id, True)
        self.__testcase = init(self.id, False)
        self.point = testcase_scores[self.id - 1]
        
    def solve(self, func, isSample):
        solving_inputs = self.sample if isSample else self.__testcase
        for i, case in enumerate(solving_inputs):
            input = case['input']
            ans = case['output']
            try:
                written_ans = func(*input)
                if type(written_ans) == tuple:
                    written_ans = list(written_ans)
                else:
                    written_ans = [written_ans]
                if written_ans != ans:
                    return i, map_input(i + 1, inspect.getfullargspec(func).args, input, ans)
            except Exception as e: 
                raise Exception("Oh no! please contact TA") from e
        return len(solving_inputs), ""


# %%
class Player:
    def __init__(self):
        self.id = uuid.uuid4()
        self.problem = [Problem(i) for i in range(1, q_num + 1)]
        self.score = [0 for _ in range(q_num)]
        self.submit_cnt = [0 for _ in range(q_num)]
        
    # 不計分測資（sample）
    def run(self, id, func):
        hint_str = ""
        pass_num, wrong_testcase = self.problem[id - 1].solve(func, True)
        if wrong_testcase:
            hint_str = f"\n\nSample {pass_num + 1} failed\n{wrong_testcase}"
        print(f"Numbers of sample passed: {pass_num}/2" + hint_str)
        
    # 計分測資（testcase）    
    def submit(self, id, func):
        hint_str = ""
        pass_num, wrong_testcase = self.problem[id - 1].solve(func, False)
        if wrong_testcase:
            hint_str = f"\n\nTestcase {pass_num + 1} failed\n{wrong_testcase}"
        print(f"Numbers of testcase passed: {pass_num}/10" + hint_str)
        self.submit_cnt[id - 1] += 1
        self.score[id - 1] = max(self.score[id - 1], pass_num * self.problem[id - 1].point)
    
    # 查看分數    
    def view_score(self):
        print("Score for each problem: ", self.score)
        print(f"Total: {sum(self.score)}")



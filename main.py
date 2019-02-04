import unittest
import read, copy
from logical_classes import *
from student_code import KnowledgeBase
import pdb

class KBTest(unittest.TestCase):

    def setUp(self):
        # Assert starter facts
        file = 'statements_kb4.txt'
        self.data = read.read_tokenize(file)
        data = read.read_tokenize(file)
        self.KB = KnowledgeBase([], [])
        for item in data:
            if isinstance(item, Fact) or isinstance(item, Rule):
                self.KB.kb_assert(item)
        
    def test1(self):
        # Did the student code contain syntax errors, AttributeError, etc.
        ask1 = read.parse_input("fact: (motherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")

    def test2(self):
        # Can fc_infer actually infer
        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")

    def test3(self):
        # Does retract actually retract things
        print('beginning of test 3\n')

        r1 = read.parse_input("fact: (motherof ada bing)") # Asserted only
        print(' Retracting', r1)

        # r1 = read.parse_input("fact: (grandmotherof ada chen)")  # i changed this
        # print('does this support anything else\n')
        # print(r1.supports_facts)

        self.KB.kb_retract(r1)
        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)

        print('the bindings returned') #really confused by this
        print(answer[0])
        print(answer[1]) #chen's relationship is inferred and should be removed

        self.assertEqual(len(answer), 1)
        self.assertEqual(str(answer[0]), "?X : felix")

    def test4(self):
        # makes sure retract does not retract supported fact
        print('beginning of test FOUR \n')

        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")

        r1 = read.parse_input("fact: (grandmotherof ada chen)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)

        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        print('is it asserted')
        print(r1.asserted)
        print('is it supported')
        print(len(r1.supported_by))

        print('length')
        print(len(answer))
        print(answer[0])

        self.assertEqual(str(answer[0]), "?X : felix")
        self.assertEqual(str(answer[1]), "?X : chen")
        
    def test5(self):
        # makes sure retract does not deal with rules
        ask1 = read.parse_input("fact: (parentof ada ?X)")
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")
        r1 = read.parse_input("rule: ((motherof ?x ?y)) -> (parentof ?x ?y)")
        print(' Retracting', r1)
        self.KB.kb_retract(r1)
        print(' Asking if', ask1)
        answer = self.KB.kb_ask(ask1)
        self.assertEqual(str(answer[0]), "?X : bing")

    def test6(self):
        # Does fc_infer successfully change supported_by, supports_facts, and supports_rules
        print('test 6')
        ask0 = read.parse_input("fact: (parentof ada bing")
        print(' Asking if', ask0)
        answer = self.KB.kb_ask(ask0)
        print(answer[0])

        ask1 = read.parse_input("fact: (grandmotherof ada ?X)")
        # print(' Asking if', ask1)
        # answer = self.KB.kb_ask(ask1)
        # self.assertEqual(str(answer[0]), "?X : felix")
        # self.assertEqual(str(answer[1]), "?X : chen")

    # def test10(self):
    #     """this student generated test ensures the inference engine is working at a basic level"""
    #     ask1 = read.parse_input("fact: (Avenger ?X)")
    #     print(' Asking if', ask1)
    #     answer = self.KB.kb_ask(ask1)
    #     self.assertEqual(str(answer[0]), "?X : profHammond")
    #     ask2 = read.parse_input("fact: (smart ?X)")
    #     print(' Asking if', ask2)
    #     answer = self.KB.kb_ask(ask2)
    #     self.assertEqual(str(answer[0]), "?X : profHammond")
    #     ask3 = read.parse_input("fact: (employable ?X)")
    #     print(' Asking if', ask3)
    #     answer = self.KB.kb_ask(ask3)
    #     self.assertEqual(str(answer[0]), "?X : profHammond")

def pprint_justification(answer):
    """Pretty prints (hence pprint) justifications for the answer.
    """
    if not answer: print('Answer is False, no justification')
    else:
        print('\nJustification:')
        for i in range(0,len(answer.list_of_bindings)):
            # print bindings
            print(answer.list_of_bindings[i][0])
            # print justifications
            for fact_rule in answer.list_of_bindings[i][1]:
                pprint_support(fact_rule,0)
        print

def pprint_support(fact_rule, indent):
    """Recursive pretty printer helper to nicely indent
    """
    if fact_rule:
        print(' '*indent, "Support for")

        if isinstance(fact_rule, Fact):
            print(fact_rule.statement)
        else:
            print(fact_rule.lhs, "->", fact_rule.rhs)

        if fact_rule.supported_by:
            for pair in fact_rule.supported_by:
                print(' '*(indent+1), "support option")
                for next in pair:
                    pprint_support(next, indent+2)



if __name__ == '__main__':
    unittest.main()

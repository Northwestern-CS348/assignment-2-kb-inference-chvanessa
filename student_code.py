import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_remove(self, fr):
        # Case 1: Fact is supported and asserted: toggle the "asserted" flag and leave it be.
        # Case 2: Fact is only supported: do nothing.
        # Case 3: Fact is only asserted:
        #       remove its support from all rules/facts involved
        #       recursively remove those fact/rule that are not asserted and no longer contains any valid support
        #       remove the fact from the KB itself.

        if isinstance(fr, Rule):
            rule = self._get_rule(fr)
            if not rule.supported_by: #if list is empty
                factlist = rule.supports_facts
                for f in factlist:
                    f.supported_by.remove(rule)
                    self.kb_remove(f)
                rulelist = rule.supports_rules
                for r in rulelist:
                    r.supported_by.remove(rule)
                    self.kb_remove(r)

                # Then remove the rule passed in
                self.rules.remove(rule)
            else: return

        elif isinstance(fr, Fact):
            fact = self._get_fact(fr)
            # Case 1
            if fact.supported_by and fact.asserted: return

            # Case 2
            elif fact.supported_by and not fact.asserted: return

            # Case 3: if fact is ONLY asserted
            elif (not fact.supported_by) and fact.asserted:
                # Dealing with rules that removed fact supports
                rlist = fact.supports_rules
                for r in rlist:
                    r.supported_by.remove(fact)
                    self.kb_remove(r)

                # Dealing with facts that removed fact supports
                flist = fact.supports_facts
                for f in flist:
                    f.supported_by.remove(fact)
                    self.kb_remove(f)

                # Remove fact from KB
                self.facts.remove(fact)

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here

        # An asserted fact should only be removed if it is unsupported.
        # Rules must never be retracted and an asserted rule should never be removed.
        # Use the supports_rules and supports_facts fields to find and adjust facts and rules that are supported by a retracted fact.
        # The supported_by lists in each fact/rule that it supports needs to be adjusted accordingly.
        # If a supported fact/rule is no longer supported as a result of retracting this fact (and is not asserted), it should also be removed.

        if isinstance(fact_or_rule, Rule): return
            # rule = self._get_rule(fact_or_rule)
            #self.kb_remove(rule)
        elif isinstance(fact_or_rule, Fact):
            # Case 1: Fact is supported and asserted: toggle the "asserted" flag and leave it be.
            # Case 2: Fact is only supported: do nothing.
            # Case 3: Fact is only asserted:
            #       remove its support from all rules/facts involved
            #       recursively remove those fact/rule that are not asserted and no longer contains any valid support
            #       remove the fact from the KB itself.

            fact = self._get_fact(fact_or_rule)
            # Case 1
            if fact.supported_by and fact.asserted:
                fact.asserted = False

            else:
                self.kb_remove(fact)
            # Case 2
            # elif fact.supported_by and not fact.asserted: return
            #
            # # Case 3
            # elif (not fact.supported_by) and fact.asserted:
            #     # Dealing with rules that removed fact supports
            #     rlist = fact.supports_rules
            #     for r in rlist:
            #         r.supported_by.remove(fact)
            #         self.kb_remove(r)
            #
            #     # Dealing with facts that removed fact supports
            #     flist = fact.supports_facts
            #     for f in flist:
            #         f.supported_by.remove(fact)
            #         self.kb_remove(f)
            #
            #     # Remove fact from KB by calling remove function
            #     self.kb_remove(fact)


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here

        possible_bindings = match(rule.lhs[0], fact.statement)
        if not possible_bindings: return
        else:
            sb = [fact, rule]  ### is this true?
            lhs_first = instantiate(rule.lhs[0], possible_bindings)
            if len(rule.lhs) == 1:
                new_rhs = instantiate(rule.rhs, possible_bindings)
                if Fact(lhs_first) in kb.facts:  #####IS THIS OK######
                    new_fact = Fact(new_rhs, sb)
                    kb.kb_assert(new_fact)

                    fact.supports_facts.append(new_fact)
                    rule.supports_facts.append(new_fact)
                    # is this syntax necessary
                    # i = kb.facts.index(fact)
                    # kb.facts[i].supports_facts.append(new_fact)
                    # j = kb.rules.index(rule)
                    # kb.rules[j].supports_facts.append(new_fact)

            else:
                rest_rule = rule.lhs[1:]
                new_lhs = []
                for r in rest_rule:
                    s_lhs = instantiate(r, possible_bindings)
                    new_lhs.append(s_lhs)
                new_rhs = instantiate(rule.rhs, possible_bindings)
                new_statement = [new_lhs, new_rhs]

                new_rule = Rule(new_statement, sb)
                kb.kb_assert(new_rule)

                i = kb.facts.index(fact)
                j = kb.rules.index(rule)

                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)
                #kb.facts[i].supports_rules.append(new_rule)
                #kb.rules[j].supports_rules.append(new_rule)

                track = False
                for n in new_lhs:
                    if Fact(n) in kb.facts: track == True
                    else:
                        track == False
                        break
                if track == True:
                    wow_fact = Fact(new_rhs, sb)
                    kb.kb_assert(wow_fact)







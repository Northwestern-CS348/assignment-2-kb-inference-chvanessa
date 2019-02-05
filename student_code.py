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
        # Helper function for kb_retract, called recursively

        # For rules
        if isinstance(fr, Rule):
            # Get actual rule from knowledge base (dunno if this is necessary)
            rule = self._get_rule(fr)
            # If NOT supported (list is empty)
            if not rule.supported_by:
                # For each fact that the rule supports, check its supported_by list
                factlist = rule.supports_facts
                for f in factlist:
                    for i in f.supported_by:
                        if rule in i: # If a [fact, rule] pair in the sb list contains the rule, then remove
                            f.supported_by.remove(i)
                    # Now recursively call kb_remove on each fact that the rule supports
                    self.kb_remove(f)
                rulelist = rule.supports_rules
                for r in rulelist:
                    for j in r.supported_by:
                        if rule in j:
                            r.supported_by.remove(j)
                    self.kb_remove(r)

                # Then remove the rule passed in
                self.rules.remove(rule)
            # This means the rule is supported
            else: return None

        # For facts
        elif isinstance(fr, Fact):

            fact = self._get_fact(fr)
            if fact == None: return

            if len(fact.supported_by) == 0:
                # Fact is not supported, remove

                # Dealing with facts that removed fact supports
                flist = fact.supports_facts
                for f in flist:
                    for i in f.supported_by:
                        if fact in i:
                            f.supported_by.remove(i)
                    self.kb_remove(f)

                rlist = fact.supports_rules
                for r in rlist:
                    for j in r.supported_by:
                        if fact in j:
                            r.supported_by.remove(j)
                    self.kb_remove(r)

                # Remove fact from KB
                self.facts.remove(fact)

            else:
                # Fact is supported and asserted: toggle asserted flag
                if fact.asserted: fact.asserted = False # set equal to false

                # If fact is ONLY supported => stays supported, do nothing
                else: return None


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

        if isinstance(fact_or_rule, Fact):
            # Possible Cases:
            # 1) Fact is supported and asserted: toggle the "asserted" flag and leave it be.
            # 2) Fact is only supported: do nothing.
            # 3) Fact is only asserted: call kb_remove to
            #       - remove its support from all rules/facts involved
            #       - recursively remove those fact/rule that are not asserted and no longer contains any valid support
            #       - remove the fact from the KB itself

            # Retrieve actual fact from knowledge base:
            if fact_or_rule in self.facts:
                fact = self._get_fact(fact_or_rule)

                # Case 1
                if fact.supported_by and fact.asserted:
                    fact.asserted = False
                # Case 2
                elif fact.supported_by and not fact.asserted: return
                # Case 3
                else:
                    self.kb_remove(fact)
            else:
                print('This fact cannot be retracted because it is not in the knowledge base')
        else:
            # IGNORE rules because they should not be retracted
            print('Error: Cannot retract rules!')


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
        sb = [fact, rule]
        if not possible_bindings: return
        else:
            # lhs_first = instantiate(rule.lhs[0], possible_bindings)
            if len(rule.lhs) == 1:
                new_rhs = instantiate(rule.rhs, possible_bindings)
                new_fact = Fact(new_rhs)
                new_fact.supported_by.append(sb) # Modify supported_by field of new fact
                if new_fact not in kb.facts: # Add in this fact if it is not already in knowledge base
                    kb.kb_assert(new_fact)

                fact.supports_facts.append(new_fact)
                rule.supports_facts.append(new_fact)

            elif len(rule.lhs) > 1:
                rest_rule = rule.lhs[1:]
                new_lhs = []
                for r in rest_rule:
                    s_lhs = instantiate(r, possible_bindings)
                    new_lhs.append(s_lhs)
                new_rhs = instantiate(rule.rhs, possible_bindings)
                new_statement = [new_lhs, new_rhs]

                new_rule = Rule(new_statement)
                kb.kb_assert(new_rule)
                new_rule.supported_by.append(sb)

                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)








import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class RuleMaker:

    BASE_URL = os.getenv("BASE_URL")
    MANDATORY = "mandatory"
    OPTIONAL = "optional"


    def __init__(self, config_path):
        file = open(config_path)
        self.configs = json.load(file)
        self.slug_rule_map = {}

    def _create_rule(self, rule):
        rule.update({
            "issuer_id": rule.get("issuer_id") or 1,
            "partner_id": rule.get("partner_id") or 1,
        })

        ruleWithID = requests.post(f"{self.BASE_URL}/rule", json=rule) 
        resp = ruleWithID.json()
        ruleID = resp["id"]

        print(f"Created RULE with id {ruleID}")
        self.slug_rule_map[ruleID["slug"]] = ruleID["id"] 
        return ruleID
    
    def _create_criterion(self, criterion):
        criterion.update({
            "issuer_id": criterion.get("issuer_id") or 1,
            "partner_id": criterion.get("partner_id") or 1,
        })

        cWithID = requests.post(f"{self.BASE_URL}/criterion", json=criterion)
        resp = cWithID.json()
        cid = resp["id"]
        print(f"Created CRITERION with id {cid}")
        return resp["id"]
    
    def _create_rcm(self, rid, cid, type):
        data = {
            "type": type,
            "state": "active"
        }
        requests.post(f"{self.BASE_URL}/rule/{rid}/criterion/{cid}", json=data)

    def _attach_internal_criterion():
        pass

    def _create_criterions(self, ruleID, criterions, type):
        for criterion in criterions:
            if criterion["type"] == "property":
                cid = self._create_criterion(criterion)
                self._create_rcm(ruleID, cid, type)

            elif criterion["type"] == "rule":
                subRuleID = criterion["rule_slug"]
                criterion["rule_id"] = subRuleID
                del criterion["rule_slug"]
                cid = self._create_criterion(criterion=criterion)
                self._create_rcm(ruleID, cid, type)

    def _create_rule_action_map(self, action_id, rule_id):
        requests.post(f"{self.BASE_URL}/action/{action_id}/rule/{rule_id}")

    def _create_config(self, config):
        rule = config["rule"]
        action_ids = config.get("action_id")
        rule_id = self._create_rule(rule)

        mandatory_criterions = config.get("mc")
        if mandatory_criterions:
            self._create_criterions(rule_id, mandatory_criterions, self.MANDATORY)

        optional_criterions = config.get("oc")
        if optional_criterions:
            self._create_criterions(rule_id, optional_criterions, self.OPTIONAL)

        if action_ids:
            for action_id in action_ids:
                self._create_rule_action_map(action_id, rule_id)


    def create_rule_configs(self):
        for config in self.configs:
            self._create_config(config)


if __name__ == "__main__":
    RuleMaker("./config.json").create_rule_configs()

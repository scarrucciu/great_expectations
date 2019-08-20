import pytest

from great_expectations.actions import (
    BasicValidationAction,
)
from great_expectations.actions.types import (
    ActionConfig,
    ActionSetConfig,
)


def test_action_config():

    ActionConfig(**{
        "module_name" : "great_expectations.actions",
        "class_name": "SummarizeAndSendToWebhookAction",
        "kwargs" : {
            "webhook": "http://myslackwebhook.com/",
            "summarization_module_name": "great_expectations.render",
            "summarization_class_name": "SummarizeValidationResultsForSlack",
        }
    })

def test_action_set_config():

    ActionSetConfig(
        # coerce_types=True, #Need to merge in fixes to LooselyTypedDataDcit before this will work.
        #TODO: We'll also need to modify LLTD to take a DictOf argument
        **{
            #TODO: This should be a dict, not a list.
            "action_list" : [
                ActionConfig(**{ #TODO: once we enable coerce_types, this can be diasbled
                    "module_name" : "great_expectations.actions",
                    "class_name": "SummarizeAndSendToWebhookAction",
                    "kwargs" : {
                        "webhook": "http://myslackwebhook.com/",
                        "summarization_module_name": "great_expectations.render",
                        "summarization_class_name": "SummarizeValidationResultsForSlack",
                    }
                }
            )]
        }
    )

def test_subclass_of_BasicValidationAction():

    # I dunno. This is kind of asilly test.

    class MyCountingValidationAction(BasicValidationAction):
        def __init__(self, config):
            super(MyCountingValidationAction, self).__init__(config)
            self._counter = 0

        def take_action(self, validation_result_suite):
            self._counter += 1

    fake_validation_result_suite = {}

    my_action = MyCountingValidationAction({})
    assert my_action._counter == 0

    my_action.take_action(fake_validation_result_suite)
    assert my_action._counter == 1
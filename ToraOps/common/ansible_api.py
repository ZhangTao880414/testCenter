#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import shutil

import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context
import logging
import common_tools as ct


logger = logging.getLogger('main.ansible_api')

#test
#hosts_file = '/home/trade/ansible/hosts'
hosts_file = '/etc/ansible/hosts'

# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_dict = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result
        #print(json.dumps({host.name: result._result}, indent=4))
        self.host_dict[host.get_name()] = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        #print(json.dumps({host.name: result._result}, indent=4))
        #self.ok_dict[host.get_name()] = result._result
        self.host_dict[host.get_name()] = {}

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
        #print(json.dumps({host.name: result._result}, indent=4))
        self.host_dict[host.get_name()] = {}


def ansible_execute(host_list,module,arg,remote_user=None):
    #host_list = ['192.168.238.21']
    #host_list = ['test213']
    # since the API is constructed for CLI it expects certain options to always be set in the context object
    #module_path=['/to/mymodules', '/usr/share/ansible]
    # context.CLIARGS = ImmutableDict(connection='smart', module_path=['/home/trade/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules'], forks=10, become=None,
    #                                 become_method=None, become_user=None, check=False, diff=False)
    context.CLIARGS = ImmutableDict(connection='smart', module_path=['/home/trade/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules'], forks=10, become=None,
                                    become_method=None, become_user=None,remote_user=remote_user,check=False, diff=False)
    # required for
    # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','
    # initialize needed objects
    loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultsCollectorJSONCallback()

    # create inventory, use path to host config file as source or hosts in a comma separated string
    inventory = InventoryManager(loader=loader, sources=hosts_file)

    # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
    # IMPORTANT: This also adds library dirs paths to the module loader
    # IMPORTANT: and so it must be initialized before calling `Play.load()`.
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
    )

    # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
    play_source = dict(
        name="Ansible Play",
        hosts=host_list,
        gather_facts='no',
        tasks=[
            dict(action=dict(module=module, args=arg)),
            #dict(action=dict(module='shell', args='ls')),
            #dict(action=dict(module='shell', args='ls'), register='shell_out'),
            #dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))),
            #dict(action=dict(module='command', args=dict(cmd='/usr/bin/uptime'))),
        ]
    )

    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Actually run it
    try:
        result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        #print("result:",result)
    except Exception as e:
        print("except:",str(e))
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
#     print_result(results_callback)
#     return results_callback

    #print(results_callback.host_dict)

# def print_result(results_callback):
    #data_dict = {"ok":{},"failed":{},"unreachable":{}}
    #res_dict = {}
    print("UP ***********")
    #print(results_callback.host_ok)
    for host, result in results_callback.host_ok.items():
        #print(host,result._result['ansible_facts'])
        ok_msg = '{0} >>> {1}'.format(host, result._result)
        logger.info(ok_msg)
        results_callback.host_dict[host]['ok'] = result._result

    print("FAILED *******")
    #print(len(results_callback.host_failed)==0)
    for host, result in results_callback.host_failed.items():
        #failed_msg = 'host:{0} >>>msg: {1} >>>stderr: {2}'.format(host, result._result['msg'],result._result['stderr'])
        #print(result._result)
        failed_msg = '{0} >>> {1}'.format(host, result._result)
        logger.error(failed_msg)
        results_callback.host_dict[host]['failed'] = result._result

    print("DOWN *********")
    for host, result in results_callback.host_unreachable.items():
        unreachable_msg = '{0} >>> {1}'.format(host, result._result)
        logger.error(unreachable_msg)
        results_callback.host_dict[host]['unreachable'] = result._result
    print("excute_ansible finished!")
    return results_callback.host_dict 

def main():
    try:
        yaml_path = './config/server_manager_logger.yaml'
        ct.setup_logging(yaml_path)
        #res_dict = ansible_execute(['192.168.238.21','192.168.238.23'],'shell','ls')
        #res_dict = ansible_execute('test213','shell','ls')
        res_dict = ansible_execute('share_server','shell','ls')
        print("res_dict:",res_dict)
        #print("ok_dict:",results_callback.ok_dict)
        #print_result(results_callback)
    except Exception:
        logger.error('Faild to run ansible_api!', exc_info=True)
        return 0
    finally:
        for handler in logger.handlers:
            logger.removeHandler(handler)



if __name__ == '__main__':
    main()
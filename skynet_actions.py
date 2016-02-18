"""skynet_actions is the actual actions available to the skynet function.

To make a new action, add a new function to this class. The docstring is
used to make the usage info available to the end user, and the name of the
function is the name of the action as exposed to the user.
"""

import datetime as _datetime
import json as _json
import skynet_api as _api


def _log(content='', function=''):
    """Write to Skynet file in /var/log with partial syslog format."""
    t = _datetime.datetime.now()

    month = t.strftime("%b")
    day = t.strftime("%d")
    time = t.strftime("%X")

    msg = ("" + month + " " + day + " " + time + " skynet:" + function + " "
           "" + content)
    with open("skylog.txt", "a") as file:
        file.write(msg)

    return ("New data written to log.")


def suspend_one(id):
    """Suspend an environment."""
    function = "suspend_one"
    msg = ("Shutting down environment - ID: " + id)
    _log(msg, function)

    data = {'runstate': 'suspended'}
    return _api.rest('/configurations/' + id + '.json', 'PUT',
                     data=data)


def put_metadata(id, content='none'):
    """Get info on metadata for specific environment. Takes 2 parameters."""
    return _api.rest('/v2/configurations/' + id + '/user_data.json', 'PUT',
                     data=content)


def get_metadata(id):
    """Get info on metadata for specific environment."""
    return _api.rest('/v2/configurations/' + id + '/user_data.json')


def purge_metadata(_=None):
    """Purge metadata from all environments."""
    env_list = _json.loads(env_full())

    content = {"contents": ""}

    print ("Are you sure you want to do this? All metadata will be erased.")
    print ("Uncomment the code in purge_metadata if you want to continue.")

    # for i in env_list:
    #     put_metadata(i["id"], content)

    return ("Job\'s done.")


def check_comments_metadata(id):
    """Check comments from environment metadata and fix them if necessary."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. ",
                         "Please see http://pyyaml.org/wiki/",
                         "PyYAMLDocumentation for more information.")
        exit(1)

    contents = yaml.load(get_metadata(id))["contents"]

    lines = contents.split("\n")

    new_content = ""

    comments = ["# Invalid entries will be reset.",
                "# See related Confluence metadata page for help.",
                "# Ex.: \"3\" = 3 A.M. UTC",
                "# Number of days remaining before shutdown, max 31"]

    for i in range(len(comments)):
        if not lines[i].endswith(comments[i]):
            new_content += ("" + lines[i].rsplit("#")[0] + comments[i] + "\n")
        else:
            new_content += ("" + lines[i] + "\n")

    for i in range(len(comments), len(lines)):
        new_content += ("" + lines[i] + "\n")

    new_content = new_content[:-1]

    if contents != new_content:
        data = {"contents": new_content}
        put_metadata(id, data)

    return new_content


def init_metadata(_=None):
    """Initialize shutdown_delay and shutdown_time for metadata."""
    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. ",
                         "Please see http://pyyaml.org/wiki/",
                         "PyYAMLDocumentation for more information.")
        exit(1)

    env_list = _json.loads(env_full())

    for i in env_list:
        data = yaml.load(get_metadata(i["id"]))

        # If there's no metadata, create the template.
        if not data["contents"]:
            data["contents"] = ("# Invalid entries will be reset.\n"
                                "# See related Confluence metadata page for "
                                "help.\n"
                                "shutdown_time: 3 # Ex.: \"3\" = 3 A.M. UTC\n"
                                "shutdown_delay: 0 # Number of days remaining "
                                "before shutdown, max 31\n")
            put_metadata(i["id"], data)
            continue

        # This will store updated content
        new_content = ""

        contents = data["contents"]

        if "shutdown_time" not in contents:
            new_content += ("shutdown_time: 3 # Ex.: \"3\" = 3 A.M. UTC\n")

        if "shutdown_delay" not in contents:
            new_content += ("shutdown_delay: 0 # Number of days remaining "
                            "before shutdown, max 31\n")

        new_content += ("" + contents)

        if data["contents"] != new_content:
            #print ("Metadata for " + i["name"] + " - ID: " + i["id"] + " has "
            #       "existing data. Appending template...")
            data["contents"] = new_content
            put_metadata(i["id"], data)
        else:
            #print ("Metadata for " + i["name"] + " - ID: " + i["id"] + " has "
            #       "not been changed (up-to-date).")
            continue


def check_metadata(_=None):
    """Get metadata of all environments and act based on the data written."""

    try:
        import yaml
    except ImportError:
        sys.stderr.write("You do not have the 'yaml' module installed. ",
                         "Please see http://pyyaml.org/wiki/",
                         "PyYAMLDocumentation for more information.")
        exit(1)

    env_list = _json.loads(env_full())

    date = _datetime.datetime.utcnow()
    time = date.hour

    function = "check_metadata"

    perm_exclusions_count = 0
    shut_down_count = 0
    invalid_count = 0

    msg = (" ---- START: " + str(date.hour) + ":" + str(date.minute) + " UTC\n")
    _log(msg, function)

    for i in env_list:
        # Check values of shutdown_delay and shutdown_time and act based on
        # them (shut down environment, count down delay, etc.)
        try:
            check_comments_metadata(i["id"])

            data = yaml.load(get_metadata(i["id"]))

            contents = yaml.safe_load(data["contents"])
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            msg = ("Invalid YAML in " + i["name"] + " - ID: "
                   "" + i["id"] + "! Sending error report.\n")
            _log(msg, function)
            invalid_count += 1
            continue

        # Check if this is an un-templated environment (no shutdown_delay or
        # shutdown_time).
        # If you run update_metadata, this error should never be encountered.
        if (not contents or "shutdown_time" not in data["contents"] or
                "shutdown_delay" not in data["contents"]):
            msg = ("In " + i["name"] + " - ID: " + i["id"] + ": Missing "
                   "shutdown_time and/or shutdown_delay. Run update process"
                   " to fix.\n\n")
            _log(msg, function)
            continue

        # "-" in shutdown_time means permanent exclusion.
        if not contents["shutdown_time"]:
            msg = ("Permanent exclusion for " + i["name"] + " - ID: "
                   "" + i["id"] + " found. Skipping...\n")
            _log(msg, function)
            perm_exclusions_count += 1
            continue

        # Is shutdown_time valid?
        try:
            # Check if shutdown_time is not a valid time
            if (int(contents["shutdown_time"]) > 23 or
                    int(contents["shutdown_time"] < 0)):
                sd_time = str(contents["shutdown_time"])
                data["contents"] = data["contents"].replace("shutdown_time: "
                                                            "" + sd_time,
                                                            "shutdown_time: 3")
                put_metadata(i["id"], data)
        except ValueError:
            sd_time = str(contents["shutdown_time"])
            data["contents"] = data["contents"].replace("shutdown_time: "
                                                        "" + sd_time,
                                                        "shutdown_time: 3")
            put_metadata(i["id"], data)

        # Is shutdown_delay valid?
        try:
            int(contents["shutdown_delay"])
        except ValueError:
            delay = contents["shutdown_delay"]
            data["contents"] = data["contents"].replace("shutdown_delay: "
                                                        "" + delay,
                                                        "shutdown_delay: 0")
            put_metadata(i["id"], data)

        # This will load the current contents after the changes made above.
        contents = yaml.load(data["contents"])

        # Is it shutdown time?
        if int(contents["shutdown_time"]) == time:
            # If delay is 0, shut it down.
            if int(contents["shutdown_delay"]) == 0:
                suspend_one(i["id"])
                shut_down_count += 1
                continue
            # If delay above 0 and equal to/under 31, decrement by 1.
            elif (int(contents["shutdown_delay"]) <= 31 and
                    int(contents["shutdown_delay"]) > 0):
                delay = int(contents["shutdown_delay"])
                data["contents"] = data["contents"].replace("shutdown_delay: "
                                                            "" + str(delay),
                                                            "shutdown_delay: "
                                                            "" + str(delay - 1))
                put_metadata(i["id"], data)
                continue

        # If it is not shutdown time or neither of the above checks passed,
        # do these checks.

        # If delay is a negative number, change delay to 0 and do not shut down.
        if int(contents["shutdown_delay"]) < 0:
            delay = int(contents["shutdown_delay"])
            data["contents"] = data["contents"].replace("shutdown_delay: "
                                                        "" + str(delay),
                                                        "shutdown_delay: 0")
            put_metadata(i["id"], data)
            continue
        # Else, if delay > 31, change to 31.
        elif int(contents["shutdown_delay"]) > 31:
            delay = int(contents["shutdown_delay"])
            data["contents"] = data["contents"].replace("shutdown_delay: "
                                                        "" + str(delay),
                                                        "shutdown_delay: 31")
            put_metadata(i["id"], data)
            continue

    _log("Environments suspended: " + str(shut_down_count), function)
    _log("Permanent exclusions found: " + str(perm_exclusions_count), function)
    _log("Invalid metadata instances caught: " + str(invalid_count), function)


def update_metadata(_=None):
    """Run metadata processes in intended order (to be run every hour)."""
    init_metadata()
    check_metadata()
    return ("Job\'s done.")


def vm_detail(vm_id):
    """Get the detailed information from a VM id."""
    return _api.rest('/vms/' + vm_id)


def projects(_):
    """Get info on the projects and environments in them."""
    return _api.rest('/v2/projects?count=100&offset=0')


def project(project_id):
    """Get info on the specifed project id."""
    return _api.rest('/v2/projects/' + project_id)


def project_full(project_id):
    """Get configuration info on the specifed project id."""
    return _api.rest('/v2/projects/' + project_id + '/configurations/')


def exclusions(_):
    """Get list of exclusions from the exclusions file.

    This action doesn't query the API, but instead looks for the
    exclusions-final.conf file in the control_dir
    (specified in the config.yml).
    This file should be updated from git regularly, so here we're just reading
    the current contents to know what machines should not be suspended.
    See the exclusions file for details on its format.
    """
    exclusion_list = []
    exclusions_file = open(_api.control_dir + '/exclusions-final.conf', 'r')
    for line in exclusions_file:
        exclusion_list.append(line.split("#", 1)[0].rstrip())

    exclusion_list = [item for item in exclusion_list if item]
    # was: = filter(None, exclusions)

    # encode exclusions in unicode
    unicode_exclusions = [unicode(i) for i in exclusion_list]

    return unicode_exclusions


def suspend(_):
    """Suspend the appropriate configurations.

    This takes a set of the environments (see action env for a sample list) and
    removes any environment in the exclusion list (see action exclusions for a
    sample list) and then issues a suspend command.
    Warning: This action will actively suspend environments. If exclusions is
    not up to date, this could suspend everything in skytap.
    """
    configurations = set(_json.loads(env()))
    exclusion_list = set(exclusions(None))
    suspends = list(configurations - exclusion_list)

    data = {'runstate': 'suspended'}

    for i in suspends:
        print('Suspending environment: ' + i)
        _api.rest('/configurations/' + i + '?runstate=suspended',
                  'PUT', data=data)


def vpns(_=None):
    """Get list of all VPNs.

    Gets details for global VPN settings.
    """
    return _api.rest('/vpns.json')


def vpn(vpn_id):
    """Get list of one VPN detail set.

    Gets details for one VPN's info.
    """
    return _api.rest('/vpns/' + vpn_id)


def env(_=None):
    """Return a simple list of environments (configurations).

    Sample output:
    [
        "437940",
        "561948",
        "1111664"
    ]
    """
    json_output = _api.rest("/v2/configurations?scope=company")
    envs = []
    for j in _json.loads(json_output):
        envs.append(j['id'])
    return _json.dumps(envs, indent=4)


def env_full(_=None):
    """Return a detailed list of environments.

    Sample output:
    [
      {
        "url": "https://cloud.skytap.com/configurations/2836084",
        "error": "",
        "id": "2836084",
        "name": "XO Master"
      },
      {
        "url": "https://cloud.skytap.com/configurations/3168668",
        "error": "",
        "id": "3168668",
        "name": "XO Production"
      },
      {
        "url": "https://cloud.skytap.com/configurations/3942800",
        "error": "",
        "id": "3942800",
        "name": "XO CI Testing - IT"
      }
    ]
    """
    return _api.rest("/v2/configurations?scope=company")


def user_env(user_id):
    """Get a list of environments associated with a particular user."""
    body = _api.rest('/users/' + user_id)
    env_list = []
    jbody = _json.loads(body)
    conf = jbody.get('configurations')
    for c in conf:
        env_list.append(c.get('id'))
    return env_list


def user_env_full(user_id):
    """Get detailed environment details.

    Gets details for environments associated with a particular user_id.
    """
    body = _api.rest('/users/' + user_id)
    jbody = _json.loads(body)
    conf = jbody.get('configurations')
    return conf


def users(_=None):
    """Get the basic user list.

    Sample output:
    [
      {
        "id": "14414",
        "url": "https://cloud.skytap.com/users/14414",
        "login_name": "phaury@fulcrum.net",
        "first_name": "Paul",
        "last_name": "Haury",
        "title": "",
        "email": "phaury@fulcrum.net",
        "created_at": "2012-01-02T12:43:05-08:00",
        "deleted": false
      }
    ]
    """
    return _api.rest('/users')


def quotas(_=None):
    """Get Skytap quotas and basic info on the Skytap service.

    Sample output:
    [
      {
        "id": "concurrent_storage_size",
        "quota_type": "concurrent_storage_size",
        "units": "MB",
        "limit": 184320000,
        "usage": 103195962,
        "subscription": 122880000,
        "max_limit": 184320000
      }
    ]
    Full list of ids returned:
        concurrent_vms, concurrent_svms, cumulative_svms,
        concurrent_storage_size, concurrent_networks, concurrent_public_ips
    """
    return _api.rest('/company/quotas')


def ips(_=None):
    """Get all public IPs assigned by Skytap.

    A return will look something like the JSON below. Unused IPs
    will have an empty 'nics' variable, and used ones will include what
    nic/vm is using a public IP in the same variable.
    [
      {
        "id": "76.191.119.24",
        "address": "76.191.119.24",
        "region": "US-West",
        "nics": [
          {
            "id": "/vms/5832366/interfaces/nic-2511996-5899928-0",
            "deployed": false
          }
        ],
        "vpn_id": null
      },
      {
        "id": "76.191.119.34",
        "address": "76.191.119.34",
        "region": "US-West",
        "nics": [],
        "vpn_id": null
      }
    ]
    """
    return _api.rest('/ips')


def vms(environment):
    """Get a list of VMs for a given environment.

    A return will look something like the JSON below, including information
    on the environment itself, and detailed information on each VM in the
    environment.
    {
      "id": "4693564",
      "url": "https://cloud.skytap.com/configurations/4693564",
      "name": "XO PRD Hotfix",
      "error": "",
      "runstate": "running",
      "description": null,
      "suspend_on_idle": null,
      "routable": false,
      "vms": [
        {
          "id": "6142798",
          "name": "Load Balance",
          "runstate": "running",
          "hardware": {
          ... hardware info ...
          },
          "error": false,
          "asset_id": null,
          "interfaces": [
            {
            ... interface info ...
            }
          ],
          "notes": [],
          "labels": [],
          "credentials": [
            {
              "id": "4911248",
              "text": "40583"
            }
          ],
          "desktop_resizable": true,
          "local_mouse_cursor": true,
          "maintenance_lock_engaged": false,
          "region_backend": "skytap",
          "created_at": "2015/07/15 21:53:31 -0700",
          "can_change_object_state": true,
          "configuration_url":
                        "https://cloud.skytap.com/configurations/4693564"
        }
    }
    """
    return _api.rest('/configurations/' + environment)

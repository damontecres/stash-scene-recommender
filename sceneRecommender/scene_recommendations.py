import json
import sys
from stashapi.stashapp import StashInterface
from recommender import get_recommendations

json_input = json.loads(sys.stdin.read())
args = json_input["args"]
if "scene_id" not in args or not args["scene_id"]:
    print(json.dumps({"error": "scene_id is required"}))
    sys.exit(1)

scene_id = args["scene_id"]
stash = StashInterface(json_input["server_connection"])

config = stash.get_configuration()["plugins"]
if "sceneRecommender" in config:
    ignored_tags = config["sceneRecommender"].get("ignored_tags", "")
    if ignored_tags:
        ignored_tags = [
            int(x.strip()) for x in ignored_tags.split(",") if x.strip().isdigit()
        ]
    else:
        ignored_tags = []

output = get_recommendations(stash, scene_id, ignored_tags)
print(json.dumps({"output": output}))

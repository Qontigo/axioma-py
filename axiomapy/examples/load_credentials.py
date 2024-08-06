"""
Copyright © 2024 Axioma by SimCorp.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

"""
import json
from pathlib import Path

print(f"Current working directory: {Path.cwd()}")
credentials_path = Path(__file__).parent.joinpath("credentials", "credentials.json")
print(f"Looking for credentials.json at: {credentials_path}")

required = set(("username", "password"))

users = {}
if Path(credentials_path).is_file():
    with open(credentials_path) as read_file:
        print("Loaded the credentials from the json..")
        users = json.load(read_file)
        sample_users = users.get("SampleUsers", {})
        if sample_users is None:
            print(
                "ERROR: Could not find the credentials in SampleUsers"
                " - check the credentials file matches the sample"
            )
            raise ValueError(
                "Could not find the credentials in SampleUsers"
                " - check the credentials file matches the sample"
            )

else:
    print(
        f"ERROR: Could not find credentials to load at {credentials_path}. "
        "Ensure credentials file is available - do you need to copy the sample"
    )
    raise FileNotFoundError(
        f"Could not find credentials to load at {credentials_path}. "
        "Ensure credentials file is available - do you need to copy the sample"
    )


def get_user(user_key: str):
    user = sample_users.get(user_key, None)
    if user is None:
        print(
            f"Credentials for the user {user_key} could "
            f"not be found in {credentials_path}"
        )
        raise ValueError("User cannot be found in the credentials")
    keys = set(user.keys())
    missing = required - keys
    if len(missing) > 0:
        print(
            f"The following entries could not be found for user {user_key}"
            f': {", ".join(missing)}'
        )
        print("Check the credentials are defined correctly.")
        raise ValueError(
            f"The user does not have the required fields {', '.join(required)}"
        )

    print(f"{user_key}: {user.get('username')}")
    return user

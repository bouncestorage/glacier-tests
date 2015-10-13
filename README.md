# glacier-tests

A set of tests for the AWS Glacier service. The tests are generic and can be used against other Glacier clones.

### Requirements

Python 3

### Usage

Run ```./bootstrap``` from the root of the repository to setup ```virtualenv``` and all of the project requirements.

After this, tests can be run as follows:
```
GLACIER_TEST_CONF=./glacier-tests.conf ./virtualenv/bin/nosetests
```

#### Configuring the tests

The configuration file for ```glacier-tests``` has two sections: ```DEFAULT``` and ```glacier```.

##### DEFAULT

You can specify the options for ```port```, ```host```, and whether to use ```https```. For Amazon Glacier make sure to
use the correct endpoint for each region.

##### glacier

- ```access_key``` is the Amazon access key ID
- ```secret_key``` is the Amazon secret access key
- ```prefix``` is the prefix to be used when creating vaults during testing

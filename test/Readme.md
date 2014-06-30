Run test cases
==============
Use the following command

> mocha

Please see the test/test.js for the unit test source code.
Since we use nodejs/python/mongodb as a backend technology, 
the fitting testframework is Mocha/Chai, which we will use
for our functional tests.

Please see the attached documentation for details.


Prepare installation
===================
Do install the necessary dependencies we use the npm package manager,
which installs the libs described in the package.json .

npm install
npm install mocha -g


FAQ
===================
npm command was not found:

Please install nodejs with brew (osx) or apt-get (linux).
The npm package manager ist part of nodejs


Expected Testresult
====================

  /autocompletion
    ✓ should respond to keyword App (577ms)
    ✓ should respond to keyword App (106ms)
    ✓ should not throw error on empty request (549ms)
    ✓ should not respond to post request (104ms)
    ✓ should respond to keyword Google (110ms)
    ✓ should not respond to weird string (139ms)

  /search_entity
    ✓ should responed to google search (425ms)
    ✓ should responed to apple search (275ms)
    ✓ should respond to empty search (645ms)
    ✓ should provide documents (714ms)

  /
    ✓ should return 404 (100ms)
    ✓ should return 200 (413ms)
    ✓ should deliver the Onepage WebApp (112ms)

  /favorites
    ✓ should save favorite (432ms)
    ✓ should throw error on post favorite (99ms)
    ✓ should show favorite (398ms)


  16 passing (5s)

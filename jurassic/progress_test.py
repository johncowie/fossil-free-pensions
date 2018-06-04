from progress import FileCheckList
import os
import pytest

@pytest.fixture(autouse=True)
def teardown():
  yield
  os.remove('test_file')
  

def test_init():
  fcl = FileCheckList('test_file')
  assert fcl.has_todos() == False
  fcl.set_todos(['a', 'b', 'c'])
  assert fcl.has_todos() == True
  assert fcl.get_done() == []
  assert fcl.get_not_done() == ['a', 'b', 'c']

  assert fcl.get_next_todo() == 'a'
  fcl.mark_as_done('a')
  assert fcl.get_done() == ['a']
  assert fcl.get_not_done() == ['b', 'c']

  fcl2 = FileCheckList('test_file')
  
  assert fcl2.get_next_todo() == 'b'
  fcl2.mark_as_done('b')
  assert fcl2.get_done() == ['a', 'b']
  assert fcl2.get_not_done() == ['c']

  fcl.mark_as_done('d')
  assert fcl.get_done() == ['a', 'b']
  assert fcl.get_not_done() == ['c']

  assert fcl.get_next_todo() == 'c'
  fcl.mark_as_done('c')
  assert fcl.get_done() == ['a', 'b', 'c']
  assert fcl.get_not_done() == []

  assert fcl.get_next_todo() == None
  
  
  

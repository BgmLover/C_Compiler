class Block:
  function_node=None
  variable_map={}
  label_map={}
  #arrayMap={}
  break_label=None     #如果break，将会跳到哪个label
  continue_label=None  #如果continue，将会跳到哪个label
  goto_label=None      #如果goto，将会跳到哪个label

  def __init__(self):
    pass
emu.speedmode("normal")

net = require 'evNet'

-- Declare and set variables or functions if needed
while emu.emulating()
while true do

  -- Execute instructions for FCEUX


  --Debugging
  emu.message("Still running")
  emu.frameadvance() -- This essentially tells FCEUX to keep running
end

-- Needs ran after each nn attempt 
-- emu.softreset()

-- Need function to reset
-- table joypad.read(int player)

-- Write directy to memory
-- joypad.set(int player, table input)
-- joypad.write(int player, table input)


-- May need to use if evNet becomes bulky
-- emu.exec_count(int count, function func)

-- Idea record movie of best/worst attempts
-- Stretch goal: csv dump to graph using matplotlib
-- Stretch goal: GUI Library couuld be used to display 
-- nn on screen. --Note may need on sepreate thread of some sort.

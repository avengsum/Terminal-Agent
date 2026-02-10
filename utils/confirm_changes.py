import config


def confirmChanges(diff_txt:str):
  
  if not config.HUMAN_IN_LOOP:
    print("🤖 Auto-approving changes (autonomous mode)")
    return True

  print("\n here are the changes which are done by agent")
  print(diff_txt)
  print("\n do you want to apply these changes")
  user_input = input("Type Yes to confirm :" ).strip().lower()

  if user_input == "yes":
      return True
  else:
    print("user declined changes")
    return False
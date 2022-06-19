dt=$(date +"\%Y_\%m_\%d_\%H")
tar cvzf preupdate$dt.gz ../Gym_Cards/*
git pull https://shrewdlogarithm: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@github.com/shrewdlogarithm/Gym_Cards.git
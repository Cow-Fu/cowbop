FROM python

RUN apt update
RUN apt install -y fish \
	git \
	vim

# install neovim
RUN wget 'https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.deb'
RUN apt install ./nvim-linux64.deb

WORKDIR /root/.config/nvim
RUN wget 'https://raw.githubusercontent.com/nvim-lua/kickstart.nvim/master/init.lua'

# takes 3 times to do it for some reason
RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'
RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'
RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'

# install python lsp server
RUN nvim --headless -c "MasonInstall python-lsp-server" -c qall

# enable autocomplete of site packages
RUN sed -i 's/false/true/' /root/.local/share/nvim/mason/packages/python-lsp-server/venv/pyvenv.cfg


# install requirements
RUN pip install youtube-dl nextcord

WORKDIR /usr/src/app

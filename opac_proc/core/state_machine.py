# coding: utf-8
from datetime import datetime
from opac_proc.core.utils import Singleton
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.models import (
    MachineState,
    StateTransition,
    FiniteStateMachine,
)


class GenericState(object):
    _db = None
    state_name = ''
    model_instance = None
    _execution_started_at = None
    _execution_finished_at = None

    def __init__(self, state_name):
        self._db = get_db_connection()
        self.state_name = state_name

    def create(self, description='', is_initial_state=False, is_final_state=False):
        """
        Metodo para criar um Estado da manquina de estados.
        - O nome deve indicado no __init__
        - opcioais: descrição (default: vazio), estado incial e final (default: False)
        Levanta ValueError se já existe uma Maquina com o mesmo nome.
        """

        state = MachineState.objects.filter(name=self.state_name)
        if state.count() == 0:
            # não existe um estado com este nome, vamos criar e salvar
            data = {
                'name': self.state_name,
                'description': description,
                'is_initial_state': is_initial_state,
                'is_final_state': is_final_state,
            }
            try:
                state = MachineState(**data)
                state.save()
                state.reload()
            except Exception as e:
                raise e
            else:
                self.model_instance = state
            return self
        else:
            #  existe um estado com este nome
            raise ValueError(u'Já existe um MachineState com este nome: %s. Utilize o método "get"' % state)

    def get(self):
        if self.model_instance is None:
            state = MachineState.objects.filter(name=self.state_name)
            if state.count() == 0:
                raise ValueError(u'Erro: Não existe registro de MachineState com nome: %s. Utilize o método "create".' % self.state_name)
            elif state.count() > 1:
                raise ValueError(u'Erro: Existe muitos registros de MachineState com nome: %s. O nome deve ser único!' % self.state_name)
            else:
                self.model_instance = state
        return self

    def get_or_create(self, description='', is_initial_state=False, is_final_state=False):
        try:
            instance = self.get()
        except ValueError:
            instance = self.create(
                description=description,
                is_initial_state=is_initial_state,
                is_final_state=is_final_state)
        return instance

    def update(self, name=None, description=None, is_initial_state=None, is_final_state=None):
        new_data = {}
        if self.model_instance is None:
            self.model_instance = self.get()
        else:
            self.model_instance.reload()

        if name is not None and name != self.name:
            new_data['name'] = name

        if description is not None and description != self.description:
            new_data['description'] = description

        if is_initial_state is not None and is_initial_state != self.is_initial_state:
            new_data['is_initial_state'] = is_initial_state

        if is_final_state is not None and is_final_state != self.is_final_state:
            new_data['is_final_state'] = is_final_state

        self.model_instance.update(**new_data)
        self.model_instance.reload()

    @property
    def pk(self):
        return self.model_instance.pk

    @property
    def name(self):
        return self.model_instance.name

    @property
    def description(self):
        return self.model_instance.description

    @property
    def is_final_state(self):
        return self.model_instance.is_final_state

    @property
    def is_initial_state(self):
        return self.model_instance.is_initial_state

    @property
    def execution_started_at(self):
        return self.model_instance.execution_started_at

    @property
    def execution_finished_at(self):
        return self.model_instance.execution_finished_at

    def execute(self):
        """
        Aqui vai o código que vai realizar cada estado.
        """
        raise NotImplementedError

    def execution_wrapper(self):
        """
        Metodo chamado pela maquina de estado ao processar este estado.
        1. atualizamos o _execution_started_at com valor now()
        2. executamos o código do método: self.execute() (implementado em cada instância concreta)
        3. atualizamos o _execution_finished_at com valor now()
        4. retornamos:
            - se teve algum erro/exceção -> (False, 'Mensagem de erro')
            - se não teve erro/exceção -> (True, <retorno do execute()>)
        """

        self._execution_started_at = datetime.now()
        try:
            ret_val = self.execute()
            self._execution_finished_at = datetime.now()
        except Exception as e:
            return (False, str(e))
        else:
            self._execution_finished_at = datetime.now()
            execution_times = {
                'execution_started_at': self._execution_started_at,
                'execution_finished_at': self._execution_finished_at,
            }
            self.model_instance.modify(execution_times)
            return (True, ret_val)


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass


class GenericStateMachine(Singleton):
    _db = None
    machine_name = ''
    model_instance = None
    current_state = None
    _states = {}
    _transitions = {}
    _is_setup_ready = False
    _is_setup_checked = False

    def __init__(self, machine_name):
        self._db = get_db_connection()
        self.machine_name = machine_name

    @property
    def pk(self):
        return self.model_instance.pk

    @property
    def name(self):
        return self.model_instance.name

    @property
    def description(self):
        return self.model_instance.description

    @property
    def current_state(self):
        """
        Retorna uma tupla com o:
        - nome do estado incial
        - a instância do estado atual
        """
        if self.model_instance is None:
            return AttributeError(u'O foi associado um modelo. Utilize o metodo "get"')
        elif self.model_instance.current_state is None:
            return (None, None)  # estado atual esta indefinido
        else:
            return (
                self.model_instance.current_state.name,
                self.model_instance.current_state
            )

    @property
    def get_initial_state(self):
        if not self._states:
            raise ImproperlyConfigured(
                u'Não foi registrado nenhum estado. Verifique seu mêtodo: "setup_machine"')

        initial_states = [st for st in self._states if st.is_initial_state]

        if len(initial_states) == 0:
            raise ImproperlyConfigured(
                u'Não foi registrado nenhum estado inicial. Verifique seu mêtodo: "setup_machine"')
        elif len(initial_states) > 1:
            raise ImproperlyConfigured(
                u'Foram registrados mas de um estado inicial. Verifique seu mêtodo: "setup_machine"')
        else:
            return initial_states[0]

    @property
    def execution_started_at(self):
        return self.model_instance.execution_started_at

    @property
    def execution_finished_at(self):
        return self.model_instance.execution_finished_at

    def set_ready_to_run_status(self):
        self.model_instance.is_ready_to_run = self._is_setup_ready and self._is_setup_checked
        self.model_instance.save()

    @property
    def get_ready_to_run_status(self):
        return self._is_setup_ready and self._is_setup_checked

    def setup_machine(self):
        """
        aqui vc vai "montar" a maquina de estados,
        chamando os outros metdos da classe. Por exemplo:

        >>> # registramos os estados.
        >>> # assumindo que FooGenericState é uma especialização de GenericState
        >>>
        >>> state_initial = FooGenericState(name='state_initial')
        >>> state_2 = FooGenericState(name='state_2')
        >>> state_3 = FooGenericState(name='state_3')
        >>> state_final = GenericState(name='state_final')
        >>>
        >>> # registramos estados incial e final
        >>> self.register_initial_state(state_initial)
        >>> self.register_final_state(state_4_final)
        >>>
        >>> # registramos estados "intermedios"
        >>>
        """
        raise NotImplementedError

    def create(self, description='', current_state=None):
        """
        Metodo para criar um Estado da manquina de estados.
        - O nome deve indicado no __init__
        - opcioais: descrição (default: vazio), estado incial e final (default: False)
        Levanta ValueError se já existe uma Maquina com o mesmo nome.
        """

        machine = FiniteStateMachine.objects.filter(name=self.machine_name)
        if machine.count() == 0:
            # não existe uma maquina com este nome, vamos criar e salvar
            data = {
                'name': self.machine_name,
                'description': description,
                'current_state': current_state
            }
            try:
                machine = FiniteStateMachine(**data)
                machine.save()
                machine.reload()
            except Exception as e:
                raise e
            else:
                self.model_instance = machine
        else:
            raise ValueError(u'Já existe uma FiniteStateMachine com este nome: %s. Utilize o método "get"' % self.machine_name)

    def get(self):
        if self.model_instance is None:
            machine = FiniteStateMachine.objects.filter(name=self.machine_name)
            if machine.count() == 0:
                raise ValueError(u'Erro: Não existe uma FiniteStateMachine com nome: %s. Utilize o método "create".' % self.machine_name)
            elif machine.count() > 1:
                raise ValueError(u'Erro: Existe muitas FiniteStateMachine com nome: %s. O nome deve ser único!' % self.machine_name)
            else:
                self.model_instance = machine
        return self.model_instance

    def get_or_create(self, description='', current_state=None):
        try:
            instance = self.get()
        except ValueError:
            instance = self.create(
                description=description,
                current_state=current_state)
        return instance

    def register_state(self, state_instance):
        """
        1. Verificamos que o estado seja uma instância ou sublcasse de GenericState
        2. Verificamos que o estado não esteja registrado anteriormente
        3. Caso afirmativo, atualizaos o dict self.states com
           - o nome do `state_instance` como chanve
           - o `state_instance` como valor

           self._states[state_instance.state_name] = state_instance
        """

        if not isinstance(state_instance, GenericState):
            raise ValueError(u'O parâmetro: state_instance não é uma instância ou subclasse de: GenericState')

        name = state_instance.state_name
        if name in self._states.keys():
            raise ValueError(u'O estado com nome: %s já foi registado previamente!' % name)
        else:
            self._states[name] = state_instance

    def register_transition(self, from_state_name, on_succcess_state_name, on_failure_state_name):
        """
        1. Validamos que cada estado (from, on_succcess, on_failure) estejam registados em self._states
        2. Verificamos que o estado correspondente com `from_state_name` não é estado final.
           Não da para definir uma transição partido de um estado final.
        3. Se esta tudo certo, registramos a transição
        4. Salvamos as mudanças
        """

        # validamos que cada estado (from, success e failure) estejam registrados em `self._states`
        registered_states_names = [state[0] for state in self._states]
        for st_name in [from_state_name, on_succcess_state_name, on_failure_state_name]:
            if st_name not in registered_states_names:
                raise ValueError(u'O estado %s não foi registado. Utilize o método: register_state.' % registered_states_names)

        from_state_instance = self._states[from_state_name]
        succcess_state_instance = self._states[on_succcess_state_name]
        failure_state_instance = self._states[on_failure_state_name]

        if from_state_instance.is_final_state:
            raise ValueError(u'Não é possível registar uma transição partindo de um state que é final.')

        transition_dict = {
            'on_success': succcess_state_instance,
            'on_failure': failure_state_instance,
        }
        self._transitions[from_state_name] = StateTransition(**transition_dict)

    def check_machine_setup(self):
        """
        Validamos que a FSM esta bem configurada:
        - tem 1 estado inicial registado
        - tem pelo menos 1 estado final registrado
        - tem transição entre todos os estado registados
            -  1. não deve ter transições partindo de estados finais
            -  2. deve ter pelo menos uma transição do estado inicial
            -  3. todos os estados registrados (excluindo o inicial e os finais) devem ter transição

        Resultado:
        - Se esta tudo OK, retornamos uma tupla com: (True. [])
        - Se tem erros, retornamos uma tupla com: (False, ['lista', 'com', 'os', 'erros'] )
        """
        initial_state = None
        final_states = []
        error_list = []
        for st in self._states:
            # verificamos se foi definido um e só um estado incial'
            if st.is_initial_state and initial_state is None:
                initial_state = st
            else:
                error_list.append('Existe mais de um estado inicial')

            # coletamos os estados finais
            if st.is_final_state:
                final_states.append(st)

        # verificamos se foi definido pelo menos um estado final'
        if len(final_states) == 0:
            error_list.append('Não foi definido nenhum estado final')

        # verificamos as transições
        # -  1. não deve ter transições partindo de estados finais:
        final_states_names = [final_states.state_name for st in final_states]
        for final_st_name in final_states_names:
            if final_st_name in self._transitions.keys():
                error_list.append("Tem uma transição partindo de um estado final: %s" % final_st_name)

        # -  2. deve ter pelo menos uma transição do estado inicial:
        initial_state_name = initial_state.state_name
        if initial_state_name not in self._transitions.keys():
                error_list.append("Não tem transição partindo do estado inicial: %s" % initial_state_name)

        # - 3. todos os estados registrados (excluindo o inicial e os finais) devem ter transição
        normal_states = [st for st in self._states if not st.is_initial_state and not st.is_final_state]
        normal_states_name = [st.state_name for st in normal_states]
        for normal_state_name in normal_states_name:
            if normal_states_name not in self._transitions.keys():
                error_list.append("Não tem transição partindo de este estado: %s" % normal_states_name)

        # retornamos os resultados
        if len(error_list) > 0:
            return (False, error_list)
        else:
            return (True, [])

    def reset_to_initial_state(self):
        """
        Muda o atributo: `current_state` para o estado inicial.
        """

        self.current_state = self.get_initial_state()

    def engine_start(self):
        self.get_or_create()
        if not self._setup_ready:
            self.setup_machine()
            self._setup_ready = True

        is_setup_ok, setup_errors = self.check_machine_setup()
        if is_setup_ok:
            self._is_setup_ready = self._is_setup_checked = True
            self.set_as_ready_to_run()
        else:
            self._is_setup_ready = True
            self._is_setup_checked = True
            self.set_as_ready_to_run()
            raise ImproperlyConfigured(
                'Machine (name: %s) setup has erros: %s' % (
                    self.machine_name, setup_errors))

        self.reset_to_initial_state()

    def one_step_forward(self):
        pass

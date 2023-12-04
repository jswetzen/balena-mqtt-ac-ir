from subprocess import run


class IRSender:
    def __init__(
        self,
        ir_config: str = "my-fujitsu-heater.toml",
        send_repeat: int = 10,
    ) -> None:
        self.ir_config = ir_config
        self.send_repeat = send_repeat
        self._ir_device = None

    @property
    def ir_device(self):
        if self._ir_device is None:
            led_run = run(["ir-ctl", "-f", "-d", "/dev/lirc0"], capture_output=True)
            ir_id = 0 if led_run.stdout.decode().find("can send") > -1 else 1
            self._ir_device = f"/dev/lirc{ir_id}"
        return self._ir_device

    def send_key(
        self,
        key: str,
    ):
        send_result = 0
        for _ in range(self.send_repeat):
            send_result += run(
                ["ir-ctl", "-k", self.ir_config, "-K", key, "-d", self.ir_device],
                capture_output=True,
            ).returncode
        return send_result == 0


